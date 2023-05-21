import matplotlib.pyplot as plt

if __name__ == '__main__':
    fig,ax = plt.subplots(2,2, figsize=(12,8))
    ax[0,0].plot([0,1,3,5,7], [1,5,7,8,3])

    txt = ax[1,0].text(0, 0, 'Hi!', fontsize=18.)
    txt.set_text('Release yodelf')

    plt.show()