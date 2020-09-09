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

## How it works

I could have used image processing techniques to find the blob that make up each key (but then I wouldn't have the cool side effect of this program!). Instead I built a huge map of colors, and then applied that map to the template image. 

This map is: \
pixel_color_from_template -> average_pixel_color_from_colors_image. 

where the pixels chosen for each average are the pixels that occur at the same (x, y) location as the template pixel. (I would resize the colors image to match the size of the template image). 



[keyboard]: https://imgur.com/QnU4Kfz.png
[mountain]: https://imgur.com/AygvH4U.png
[mountain_on_keyboard]: https://imgur.com/NFv9Ooh.png


[mountain_on_circles]: https://imgur.com/TvKNGwI.png
[circles]: https://imgur.com/iVTFbu6.png

[example_template]: example_template.png
[example_colors]:
[example_result]:
