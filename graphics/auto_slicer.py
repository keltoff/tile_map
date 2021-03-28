

img = load_image
b_img = binarize(img)

components = np.ndarray(b_img.shape, int)
alias = []
comps = 0

for x, y, filled, l_comp, u_comp in scan_lines(b_img):
    if filled:
        if l_comp and u_comp:
            alias.append(l_comp, u_comp)
        if l_comp:
            c = l_comp
        elif u_comp:
            c = u_comp
        else:
            comps += 1
            c = comps

        components[x, y] = c
    else:
        components[x, y] = 0

# merge aliases

# compute bbs

# output