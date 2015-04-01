from django.db import models

class Image(models.Model):
    imgfile = models.ImageField()

    def __unicode__(self):
        return "id: " + str(self.id) + ", url: " + self.imgfile.url
