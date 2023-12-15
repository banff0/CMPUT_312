import numpy as np
import cv2
from models import ViT, ClassificationHead, CNN
from torchvision.transforms import Compose, ToTensor, Normalize, RandomRotation
import torch

class LetterDetection(): 
    def __init__(self, verbose=False):
        # The labels for our dataset in the correct order
        self.labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
          'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
          'a', 'b', 'd', 'e', 'f', 'g', 'h', 'n', 'q', 'r', 't']
        # hyper params for the ViT model
        self.num_classes = 47
        self.image_size = 28
        self.in_channels = 1
        self.patch_size = 4
        self.hidden_size = 64
        self.layers = 6
        self.heads = 8
        self.embed_size = 64
        
        self.verbose = verbose
        self.max_attempts = 500 # max times we will re-predict if we predict a number
        self.num_votes = 11 # number of predictions to make per image

        # how we split the dataset 
        # self.split = "bymerge"
        self.split = "balanced"
        # how much we inflate the sizee of each letter
        self.dilation_size = 2

        # load the pre-trained CNN model
        self.CNN_model = CNN(1, self.num_classes)
        weights = torch.load(f"saved_models/EMNIST{self.split}_CNN_no_rot.pt")
        self.CNN_model.load_state_dict(weights["model"])
        print(f"Validation accuracy of the loaded model is : {weights['acc']}")
        self.CNN_model.eval()

        # load the pre-trained ViT model
        self.vit_model = ViT(image_size=self.image_size, patch_size=self.patch_size, num_channels=self.in_channels, hidden_size=self.hidden_size, layers=self.layers, heads=self.heads)
        self.classifier_model = ClassificationHead(hidden_size=self.vit_model.hidden_size, num_classes=self.num_classes)

        checkpoint = torch.load("saved_models/vit_classifier_EMNIST_balanced.pt")
        if self.verbose: print(checkpoint["classifier"]["classifier.weight"].shape)
        self.vit_model.load_state_dict(checkpoint["vit"])
        self.classifier_model.load_state_dict(checkpoint["classifier"])
        self.vit_model.eval()
        self.classifier_model.eval()

        # the transformations that should be done to our input images
        self.transform = Compose([
            ToTensor(),
            RandomRotation([-15, 15]),
            Normalize((0.5, ), (0.5, )),
            ])
        
    def get_img(self, path):
        """
        Read an image from path, and prepare it for finding letters
        """
        # get the image in grayscale
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        # Perform a dilation on the image to inflate the size of the letters
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (2 * self.dilation_size + 1, 2 * self.dilation_size + 1), (self.dilation_size, self.dilation_size))
        img = cv2.erode(img, element)
        # Get all the pixels within a certain colour range
        thresh = cv2.inRange(img, 0, 80)
        # display the processed image
        if self.verbose:
            cv2.imshow("titl", thresh)
            cv2.waitKey(0) 
            cv2.destroyAllWindows()
        return thresh
        
    
    def get_bbox(self, img):
        # get the countours from the image
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_poly = [None]*len(contours)
        boundRects = [None]*(len(contours))

        # get all the bounding boxes, and their coresponding letter contours
        for i, c in enumerate(contours):
            contours_poly[i] = cv2.approxPolyDP(c, 3, True)
            boundRects[i] = [*cv2.boundingRect(contours_poly[i]), c]

        # sort them from leftmost to rightmost
        boundRects.sort(key=lambda rect: rect[0])
        return boundRects
    
    def make_pred(self, img, boundRects):
        word = ""
        word2 = ""
        last_rect_tl = 0
        # make a prediction for each detected letter
        for i in range(len(boundRects)):
                # only consider large bounding boxes to avoid noise in image
                if boundRects[i][2] * boundRects[i][3] > 800:
                    # avoid looking at sub components of words
                    if boundRects[i][0] + boundRects[i][2] < last_rect_tl:
                        continue 
                    last_rect_tl = boundRects[i][0] + boundRects[i][2]

                    # pad the letter image borders
                    boundRects[i][:-1] += np.array([-15, -15, 30, 30])
                    # create a blank image for the letters to sit on
                    letter_img = np.zeros_like(img)
                    # draw the letter onto the blank image
                    cv2.drawContours(letter_img, [boundRects[i][4]], 0, [255, 255, 255], 5)
                    # only take the portion of the image with the letter and blur for better model accuracy
                    letter_img = letter_img[int(boundRects[i][1]):int(boundRects[i][1]+boundRects[i][3]), int(boundRects[i][0]):int(boundRects[i][0]+boundRects[i][2])]
                    letter_img = cv2.blur(letter_img,(5,5))

                    # show letter image
                    if self.verbose:
                        cv2.imshow("titl", letter_img)
                        cv2.waitKey(0) 
                        cv2.destroyAllWindows()   

                        cv2.imshow("titl", cv2.rotate(cv2.resize(letter_img, (28, 28)), cv2.ROTATE_90_CLOCKWISE))
                        cv2.waitKey(0) 
                        cv2.destroyAllWindows()

                    # no autograd
                    with torch.no_grad():                        
                        pred = 0
                        attempts = 0
                        # keep making preds if we predict a number since we don't do numbers
                        while pred < 10 and attempts < self.max_attempts:
                            # create N copies of the image and apply the nesciary transformations
                            images = torch.ones([self.num_votes, 1, 28, 28])
                            for i in range(self.num_votes):
                                # rotate the image since the training data was rotated
                                rot_img = cv2.rotate(cv2.resize(letter_img, (28, 28)), cv2.ROTATE_90_CLOCKWISE)
                                images[i][0] = self.transform(rot_img)
                            # make N predictions 
                            out = self.CNN_model(images)
                            _, preds = torch.max(out.data, 1)

                            if self.verbose:
                                for pred in preds:
                                    print(self.labels[pred])
                                print("#################")
                            
                            # get the most common prediction
                            pred, _ = torch.mode(preds)
                            # take care of numbers that look like letters
                            pred = self.num_to_letter(pred)
                            if self.verbose: print(f"CNN PRED: {self.labels[pred]}")
                            attempts += 1
                        # add each letter to the final word
                        word += self.labels[pred]

                        #########################################################################################
                        # NOTE These predictions are only to show how the output of the ViT compares to the CNN #
                        #      None of these predictions have any effect on the final word that is outputed     #
                        #########################################################################################
                        # same as above but now for ViT
                        feats = self.vit_model(images)
                        preds = self.classifier_model(feats)
                        _, preds = torch.max(preds.data, 1)

                        
                        for pred in preds:
                            if self.verbose: print(self.labels[pred])
                        pred, _ = torch.mode(preds)
                        # take care of numbers that look like letters
                        pred = self.num_to_letter(pred)
                        if self.verbose: print(f"VIT PRED: {self.labels[pred]}")
                        if self.verbose: print("#################")
                        word2 += self.labels[pred]
        if self.verbose:
            print(word.upper(), word2.upper())
        # return the predicted word
        return word.upper()
     
    def num_to_letter(self, pred):
        # convert number that look like letters
        # S's look like 5's
        if pred == 5:
            return 28
        # O's look like 0's
        elif pred == 0:
            return 24
        # 1's look like l's
        elif pred == 1:
            return 21
        return pred
    
    def get_word_from_image(self, path='text.jpg'):
        # load the image, get the bounding boxes, and make predictions
        img = self.get_img(path)
        bboxes = self.get_bbox(img)
        word = self.make_pred(img, bboxes)

        return word

if __name__ == "__main__":
    detector = LetterDetection()

    print(f"PREDICTION: {detector.get_word_from_image('text.jpg')}")
