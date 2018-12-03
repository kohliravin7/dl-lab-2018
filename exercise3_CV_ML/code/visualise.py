import matplotlib.pyplot as plt

plt.figure(figsize=(10, 10))

PATH = './checkpoints/'
for i in range(4):
    IoU = []
    epoch = []
    with open(PATH+'Configuration%d/testIoU.txt' % (i+1), 'r') as f:
        lines = f.readlines()
        for line in lines:
            IoU.append(float(line.split()[1]))
            epoch.append(int(line.split()[0])/1000)
    plt.plot(epoch, IoU, label='Configuration%d' % (i+1), linewidth=7.0)

plt.legend(loc='best')
plt.xlabel("Epochs(x1000)")
plt.ylabel("Intersection over Union")
plt.title('Intersection over Union vs Epochs')
plt.show()