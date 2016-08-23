from django.db import models

from django.utils.translation import ugettext_lazy as _

from taggit.models import TagBase, GenericTaggedItemBase

from uuslug import uuslug


class Tag(TagBase):
    def slugify(self, tag, i=None):
        slug = uuslug(tag,
                      instance=self,
                      max_length=100,
                      start_no=2,
                      word_boundary=True,
                      save_order=True)
        if not slug:
            slug = uuslug(tag + '_tag',
                          instance=self,
                          max_length=100,
                          start_no=2,
                          word_boundary=True,
                          save_order=True)

        slug = slug.lower()

        if i is not None:
            slug += "_%d" % i

        return slug

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ("name",)


class TaggedItem(GenericTaggedItemBase):
    tag = models.ForeignKey(Tag,
                            related_name='%(app_label)s_%(class)s_items')
