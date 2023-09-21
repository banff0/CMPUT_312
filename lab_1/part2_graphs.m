close all;
clear;
clc;

%% Straight Line
power_high = [83.5 83.5 83.5];
% measurements_high[0] contains actual measurements, whereas 
% measurements_high[1] contains sensor measurements
measurements_high = [[18.5 18.6 18.9]; 
                     [16.9 17.6 17.6]];
percentage_error_high = zeros(1, 3);
for j = 1:3
    percentage_error_high(j) = (abs(measurements_high(1, j)-measurements_high(2, j))/measurements_high(1, j)) * 100;
end

power_low = [21 21 21];
% measurements_low[0] contains actual measurements, whereas 
% measurements_low[1] contains sensor measurements
measurements_low = [[17.3 17.4 17.2]; 
                    [17.3 17.6 16.9]];
percentage_error_low = zeros(1, 3);
for j = 1:3
    percentage_error_low(j) = (abs(measurements_low(1, j)-measurements_low(2, j))/measurements_low(1, j)) * 100;
end

power = zeros(1, 6);
power(1:3) = power_low;
power(4:6) = power_high;
percentage_error = zeros(1, 6);
percentage_error(1:3) = percentage_error_low;
percentage_error(4:6) = percentage_error_high;

hold on;
scatter(power, percentage_error, 'Marker', 'x');
xlabel('Percentage Power'); ylabel('Percentage Error');

coefficients = polyfit(power, percentage_error, 1);
m = coefficients(1);
b = coefficients(2);
plot(power, m * power + b, 'r');
hold off;