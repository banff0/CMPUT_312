import numpy as np
import cv2
from models import ViT, ClassificationHead, CNN
from torchvision.transforms import Compose, ToTensor, Normalize, RandomRotation
import torch

class LetterDetection(): 
    def __init__(self):
        self.labels = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
          'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
          'a', 'b', 'd', 'e', 'f', 'g', 'h', 'n', 'q', 'r', 't']
        self.num_classes = 47
        self.image_size = 28
        self.in_channels = 1
        self.patch_size = 4
        self.hidden_size = 64
        self.layers = 6
        self.heads = 8
        self.embed_size = 64

        self.verbose = True
        self.max_attempts = 500
        self.num_votes = 11
        # self.split = "bymerge"
        self.split = "balanced"

        self.dilation_size = 2

        self.CNN_model = CNN(1, 47)
        weights = torch.load(f"..\\EMNIST{self.split}_CNN_no_rot.pt")
        # print(weights["model"].items())
        self.CNN_model.load_state_dict(weights["model"])
        print(weights["acc"])
        self.CNN_model.eval()

        self.CNN_model_2 = CNN(1, 47)
        weights = torch.load(f"..\\EMNIST{self.split}_CNN.pt")
        # print(weights["model"].items())
        self.CNN_model_2.load_state_dict(weights["model"])
        print(weights["acc"])
        self.CNN_model_2.eval()

        self.vit_model = ViT(image_size=self.image_size, patch_size=self.patch_size, num_channels=self.in_channels, hidden_size=self.hidden_size, layers=self.layers, heads=self.heads)
        self.classifier_model = ClassificationHead(hidden_size=self.vit_model.hidden_size, num_classes=self.num_classes)

        checkpoint = torch.load("..\\vit_classifier_EMNIST_balanced.pt")
        if self.verbose: print(checkpoint["classifier"]["classifier.weight"].shape)
        self.vit_model.load_state_dict(checkpoint["vit"])
        self.classifier_model.load_state_dict(checkpoint["classifier"])
        self.vit_model.eval()
        self.classifier_model.eval()

        self.transform = Compose([
            # torchvision.transforms.Lambda(rotate_and_flip),
            ToTensor(),
            RandomRotation([-15, 15]),
            Normalize((0.5, ), (0.5, )),
            ])
        
    def get_img(self, path):
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        # img = cv2.normalize(img, np.zeros_like(img), 0, 255, cv2.NORM_MINMAX)
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (2 * self.dilation_size + 1, 2 * self.dilation_size + 1), (self.dilation_size, self.dilation_size))

        img = cv2.erode(img, element)
        thresh = cv2.inRange(img, 0, 80)
        if self.verbose:
            cv2.imshow("titl", thresh)
            cv2.waitKey(0) 
            cv2.destroyAllWindows()
        return thresh
        
    
    def get_bbox(self, img):
        # get the countours from the image
        contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_poly = [None]*len(contours)
        boundRects = [None]*(len(contours))

        # get all the bounding boxes, and their coresponding letters
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
        for i in range(len(boundRects)):
                # only consider large bounding boxes to avoid noise in img
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
                    cv2.drawContours(img, [boundRects[i][4]], 0, [255, 255, 255], 5)
                    # only take the potion of the image with the letter and blur for better model acc
                    letter_img = letter_img[int(boundRects[i][1]):int(boundRects[i][1]+boundRects[i][3]), int(boundRects[i][0]):int(boundRects[i][0]+boundRects[i][2])]
                    letter_img = cv2.blur(letter_img,(5,5))

                    # show letter image
                    if self.verbose:
                        # Used for generating some images for the report
                        # cv2.imshow("titl", img[int(boundRects[i][1]):int(boundRects[i][1]+boundRects[i][3]), int(boundRects[i][0]):int(boundRects[i][0]+boundRects[i][2])])
                        # cv2.waitKey(0) 
                        # cv2.destroyAllWindows()
                        # cv2.imwrite(f"img_{i}.jpg", img[int(boundRects[i][1]):int(boundRects[i][1]+boundRects[i][3]), int(boundRects[i][0]):int(boundRects[i][0]+boundRects[i][2])]) 

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
                        # keep making preds if we get a number since we don't do numbers
                        while pred < 10 and attempts < self.max_attempts:
                            # create N copies of the image and apply the same transformations as in training
                            images = torch.ones([self.num_votes, 1, 28, 28])
                            for i in range(self.num_votes):
                                # images[i][0] = self.transform(cv2.resize(letter_img, (28, 28)))
                                images[i][0] = self.transform(cv2.rotate(cv2.resize(letter_img, (28, 28)), cv2.ROTATE_90_CLOCKWISE))
                            out = self.CNN_model(images)
                            _, preds = torch.max(out.data, 1)

                            for pred in preds:
                                if self.verbose: print(self.labels[pred])
                            if self.verbose: print("#################")
                            # get the most common prediction
                            pred, _ = torch.mode(preds)
                            # take care of numbers that look like letters
                            pred = self.num_to_letter(pred)
                            if self.verbose: print(f"CNN PRED: {self.labels[pred]}")
                            attempts += 1
                        # add each letter to the final word
                        word += self.labels[pred]

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
        return word.upper()
     
    def num_to_letter(self, pred):
        if pred == 5:
            return 28
        elif pred == 0:
            return 24
        elif pred == 1:
            return 21
        return pred
    
    def get_word_from_image(self, path='text.jpg'):
        img = self.get_img(path)
        bboxes = self.get_bbox(img)

        word = self.make_pred(img, bboxes)

        return word

if __name__ == "__main__":
    detector = LetterDetection()

    print(f"PREDICTION: {detector.get_word_from_image('text.jpg')}")














