from PIL import ImageFilter

area_1p = [876,175,1262,679]
area_2p = [20,175,406,679]
area_loveletter = [527, 449, 760, 623]

def blur(image, play_side='', loveletter=False):
    ret = image.copy()

    if play_side != '':
        if play_side == '1P':
            area_rival = area_1p
        if play_side == '2P':
            area_rival = area_2p

        rival_crop = image.crop(area_rival)
        rival_blur = rival_crop.filter(ImageFilter.GaussianBlur(10))
        ret.paste(rival_blur, (area_rival[:2]))

    if loveletter:
        loveletter_crop = image.crop(area_loveletter)
        loveletter_blur = loveletter_crop.filter(ImageFilter.GaussianBlur(10))
        ret.paste(loveletter_blur, (area_loveletter[:2]))
    
    return ret
