import numpy as np

import macro


def main():
    horizontals = [-50, -40, -30, -20, -10, 0, 10, 20, 30]
    verticals = np.arange(-20, 160, 10)

    new_macro = []

    for i, vertical in enumerate(verticals):
        horizontals.reverse()
            
        for horizontal in horizontals:
            new_macro.append((horizontal, vertical))
            new_macro.append('wait 1')

    macro.save('default', new_macro)

if __name__ == "__main__":
    main()
