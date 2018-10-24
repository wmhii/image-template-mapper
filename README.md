# Image Template Mapper

This project was originally created to find how I might color an RGB
keyboard to match the colors of my desktop background. I later did some
testing with other kinds of images and found some interesting results. 

## Intended Purpose
First, the intended purpose. I will show the two input images, the first
image provides the colors to use, and the second image provides the structure
the mapped image should follow. Then I will show the resulting mapped
image.

Colors Image\
![Mountain Image][mountain]

Template Image\
![Keyboard Template][keyboard]

Resulting Mapped Image\
![Mapped Image][mountain_on_keyboard]

This works as expected. The only issue with this implementation is that you
have to open the result in an image editor and look at the colors individually.

[keyboard]: keyboardmap.bmp
[mountain]: mountain.jpg
[mountain_on_keyboard]: mapped_image.png

## Interesting Results

I started to run the algorithm against images with no clear structure (unlike the keyboard template).
Most of the time I would get junk, and sometimes I would get something fascinating. To get 
interesting results, I believe the template needs to have higher color variety and of higher quality,
as jpeg artifacts seem to stand out a lot more.

In one case, I used the mountain image as my colors image
 and this circles image as a template

![circles][circles]

which resulted in:\
![mountain_circles][mountain_on_circles]


[mountain_on_circles]: output15.png
[circles]: abstract.png
