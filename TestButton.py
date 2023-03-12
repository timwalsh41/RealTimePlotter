import matplotlib.pyplot as plt
from matplotlib.widgets import Button

def callback(event):
    print('You pushed a button!')

if __name__ == '__main__':
    fig,ax = plt.subplots(2,2, figsize=(12,8))
    #ax[0,0].plot([0,1,3,5,7], [1,5,7,8,3])

    button_axes = fig.add_axes([0.1, 0.0375, 0.2, 0.075])
    button = Button(button_axes, "Hi")
    button.on_clicked(callback)

    plt.show()