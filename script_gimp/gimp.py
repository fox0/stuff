for i in gimp.image_list():
    l = i.layers[0]
    pdb.gimp_layer_add_alpha(l)
    pdb.gimp_by_color_select(l, (51, 51, 51), 0, CHANNEL_OP_REPLACE, TRUE, FALSE, 0, TRUE)
    s = pdb.gimp_image_get_selection(i)

