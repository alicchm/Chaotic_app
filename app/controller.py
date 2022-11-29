class Controller:
    def __init__(self, view, model):
        self.model = model
        self.view = view

    def start_encryption(self):
        self.model.cryptogram = self.model.start_encryption(self.model.im, self.model.x, self.model.p)

    def set_x(self, x):
        self.model.x = x

    def set_px(self, px):
        self.model.px = px

    def set_image(self, path):
        self.model.source_path(path)

    def set_Spx(self, Spx):
        self.model.Spx = Spx

    def set_ciphertype(self, value):
        self.model.cipher_type = value

    def get_x(self):
        return self.model.x

    def get_px(self):
        return self.model.px

    def get_image(self):
        return self.model.image

    def get_Spx(self):
        return self.model.Spx

    def get_cryptogram(self):
        return self.model.cryptogram
    
    def get_key_sensivity(self, change_value):
        return self.model.key_sensivity(change_value)

    def get_npcr(self):
        return self.model.npcr()

    def get_uaci(self):
        return self.model.npcr()

    def get_entropy(self):
        return self.model.entropy()

    def get_correlations(self):
        return self.model.correlations()