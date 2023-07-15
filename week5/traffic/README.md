# Evidence #
A single layer for convolution using a (3, 3) kernel matrix, followed by a (2, 2) pooling and a single hidden layer with 128 units resulted in an extremely low accuracy of 0.0554.

When a second layer of convolution and pooling was added, the accuracy of the model massively increased to 0.8435 while the time needed to train the model largely remained the same.

When the first layer of pooling was removed and the kernel matrix for the second convolution layer was increased to (4, 4), the accuracy further increased to 0.9754. However, the time needed to train the model sharply increased by 4 times.

Adding a second hidden layer with 128 units resulted in similar accuracy and training speed, suggesting the number of layers do not have much impact on the performance of the model.

Going back to a single hidden layer with 256 units instead, the model resulted in similar performance but increased training time.

Going back to a single hidden layer with 128 units, when pooling was completely removed, the model needed 50% more time to compile while accuracy remained the same, suggesting pooling can increase model training speed without compromising accuracy.

Readding both pooling layers and increasing the pool size to (3, 3), we find decreased accuracy and similar compile times. As such, we believe the ideal pooling size is (2, 2).

Going back to a pool size of (3, 3), we find doubling the number of filters used in both convolution layers sharply decreased accuracy to 0.0558 and double the training time needed. On the other hand, decreasing the number of filters returned accuracy levels to 0.8343 and decreased training time to half the previous set up. This implies using too many filters is detrimental to the accuracy of the model. Accuracy seems to be the highest with between 24-32 filters

Current highest accuracy: 0.9754 with 2 convolution networks (firstly by a (3, 3) kernel matrix for simpler shapes followed by a (4, 4) kernel matrix for more complex shapes), with both having 24 filters, then pooling to a (2, 2) matrix before one hidden layer of 128 units

Changing dropout did not change training time or accuracy so long as they are kept to reasonable amounts (not lower than 0.2 or above 0.75)

# Summary #
To summarise, from trying multiple configurations, some lessons were learnt. 

Using more filters in the convolutional layers result in higher training times needed, while potentially reducing accuracy if too many filters were used. Using too little filters also results in lower accuracy. The ideal number of filters seem to be around 32. 

Using 2 layers of convolution sharply increased accuracy without impacting training time. 
Pooling only after all convolution is done instead of after each convolution layer increases accuracy and compile time. Using a larger pooling size can decrease accuracy while leaving training time unchanged. 

The number of hidden layers and the number of units in the hidden layer do NOT affect the accuracy of the model (so long as reasonable amounts of units were used, likely around 128), but does affect training times (with increasing layers and units resulting in higher training times). 

So long as dropout rates were reasonable, training time and accuracy was largely unaffected.

As such, the configuration with the highest accuracy while minimising training time is as follows: 2 convolution networks (firstly by a (3, 3) kernel matrix for simpler shapes, followed by a (4, 4) kernel matrix for more complex shapes), with both having 24 filters, then pooling to a (2, 2) matrix before submitting it to a neural network with one hidden layer of 128 units and dropout of 0.5.