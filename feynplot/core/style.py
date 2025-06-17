import matplotlib as mpl

def set_style_from_dict(style_dict):
    mpl.rcParams.update(style_dict)

def reset_style():
    mpl.rcdefaults()

def get_current_style():
    return dict(mpl.rcParams)
