from django.db import models

class Image(models.Model):
    imgfile = models.ImageField(upload_to='%Y_%m_%d')

    def __unicode__(self):
        return "id: " + str(self.id) + ", url: " + self.imgfile.url
