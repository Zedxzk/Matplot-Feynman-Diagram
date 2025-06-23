import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['STCAIYUN']
plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'Times New Roman'
plt.rcParams['mathtext.it'] = 'Times New Roman'
plt.rcParams['mathtext.bf'] = 'Times New Roman'

plt.title(r'This is a test    $\mathrm{a}^2 + b^2 = \bf{c}^2$', fontsize=25)
plt.text(0.5, 0.5, r'$\mathrm{a}^2 + b^2 = \bf{c}^2$', fontsize=25)

plt.show()