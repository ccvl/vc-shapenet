import glob, os
import bpy

texture_bank = []
# Texture bank is a set of texture images
def set_search_path(search_path):
    global texture_bank
    texture_bank = []
    texture_bank += glob.glob(os.path.join(search_path, "*.jpg"))
    texture_bank += glob.glob(os.path.join(search_path, "*.png"))
    texture_bank = [os.path.abspath(v) for v in texture_bank]
    # test_texture = texture_bank[2]

# Load texture into bpy.data.images

def apply_random_texture(actor):
    pass

def load_texture_img(img_filename):
    texture_key = os.path.basename(img_filename)
    if texture_key in bpy.data.images.keys():
        return bpy.data.images[texture_key]

    img = bpy.data.images.load(img_filename)
    return img

def get_by_id(texture_id):
    key = 'texture_%d' % texture_id
    texture = bpy.data.textures.get(key)

    if texture:
        return texture
    else:
        texture = bpy.data.textures.new(name = key, type='IMAGE')
        texture_image = load_texture_img(texture_bank[texture_id])
        texture.image = texture_image
        return texture

# def apply_texture(actor, texture_img):
def apply_texture(actor, texture, scale): # 0.02
    def _update_mtl_slot(mtl_slot):
        mtl = mtl_slot.material
        if len(mtl.texture_slots) > 0:
            text_slot = mtl.texture_slots[0]
        else:
            return

        if not text_slot:
            text_slot = mtl.texture_slots.add()

        # scale = 10
        text_slot.scale[0] = scale
        text_slot.scale[1] = scale
        text_slot.scale[2] = scale
        text_slot.texture = texture
        # text = text_slot.texture
        # text.image = texture_img

        # Probably simpler to just iterate over bpy.data.materials
        # Replace the texture images

        # for mtl_slot in actor.material_slots:
            # for material in mtl_slot:

    if len(actor.material_slots) > 0:
        for mtl_slot in actor.material_slots:
            _update_mtl_slot(mtl_slot)
        # mtl_slot = actor.material_slots[0]
    else:
        return




def apply_test_texture(actor):
    texture_img = load_texture_img(test_texture)
    apply_texture(actor, texture_img)
