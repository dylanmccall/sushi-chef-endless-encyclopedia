#!/usr/bin/env python
from le_utils.constants import content_kinds
from le_utils.constants import file_formats
from le_utils.constants import format_presets
from le_utils.constants import languages
from le_utils.constants import licenses
from ricecooker.chefs import SushiChef
from ricecooker.classes import files
from ricecooker.classes import nodes
from ricecooker.classes.licenses import get_license
from ricecooker.config import LOGGER  # Use LOGGER to print messages
from ricecooker.exceptions import InvalidNodeException
from ricecooker.exceptions import raise_for_invalid_channel

CHANNEL_NAME = "Wikipedia"
CHANNEL_SOURCE_ID = "sushi-chef-endless-encyclopedia-zim-en"
CHANNEL_DOMAIN = "endlessos.org"
CHANNEL_LANGUAGE = "en"
CHANNEL_DESCRIPTION = """
Everyone should have access to the world's biggest encyclopedia. With over
800,000 articles on important events, notable people, and more, this selection
of Wikipedia content is an invaluable resource for students, teachers, and
anyone who wants to learn about the world.
"""
CHANNEL_THUMBNAIL = "data/channel-thumbnail.png"
SELECTED_ARTICLES_NODE_THUMBNAIL = "data/selected-articles-node-thumbnail.png"

class EncyclopediaChef(SushiChef):
    channel_info = {
        "CHANNEL_SOURCE_DOMAIN": CHANNEL_DOMAIN,
        "CHANNEL_SOURCE_ID": CHANNEL_SOURCE_ID,
        "CHANNEL_TITLE": CHANNEL_NAME,
        "CHANNEL_LANGUAGE": CHANNEL_LANGUAGE,
        "CHANNEL_THUMBNAIL": CHANNEL_THUMBNAIL,
        "CHANNEL_DESCRIPTION": CHANNEL_DESCRIPTION,
    }

    def construct_channel(self, *args, **kwargs):
        """
        Creates ChannelNode and build topic tree
        Args:
          - args: arguments passed in on the command line
          - kwargs: extra options passed in as key="value" pairs on the command line
            For example, add the command line option   lang="fr"  and the value
            "fr" will be passed along to `construct_channel` as kwargs['lang'].
        Returns: ChannelNode
        """
        channel = self.get_channel(
            *args, **kwargs
        )  # Create ChannelNode from data in self.channel_info

        wikipedia_100_node = self.build_zim_document(
            "https://dumps.wikimedia.org/kiwix/zim/wikipedia/wikipedia_en_100_maxi_2021-05.zim",
            title="100 Wikipedia Articles",
            description="This collection of 100 Wikipedia articles is provided to test the Kolibri Zim plugin.",
            license=get_license(
                licenses.CC_BY_SA,
                copyright_holder="Wikipedia editors and contributors",
            ),
            language=languages.getlang("en").code,
            thumbnail=files.ThumbnailFile(path=SELECTED_ARTICLES_NODE_THUMBNAIL),
        )
        channel.add_child(wikipedia_100_node)

        # TODO: At the moment, Kolibri Studio does not support files larger
        #       than 2 GB. In the future, we should be able to use the
        #       following URL instead of a placeholder:
        #       <https://download.kiwix.org/zim/.hidden/endless/wikipedia_en_endless_maxi_2021-07.zim>

        wikipedia_endless_node = self.build_zim_document(
            "data/wikipedia_en_endless_maxi_placeholder.zim",
            title="Selected Wikipedia Articles",
            description="This collection has over 800,000 Wikipedia articles on important events, notable people, and more.",
            license=get_license(
                licenses.CC_BY_SA,
                copyright_holder="Wikipedia editors and contributors",
            ),
            language=languages.getlang("en").code,
            thumbnail=files.ThumbnailFile(path=SELECTED_ARTICLES_NODE_THUMBNAIL),
        )
        channel.add_child(wikipedia_endless_node)

        raise_for_invalid_channel(channel)

        return channel

    def build_zim_document(self, http_url, language=None, **node_kwargs):
        zim_file = ZimFile(path=http_url, language=language)
        return ZimNode(source_id=http_url, files=[zim_file], **node_kwargs)


class ZimFile(files.DownloadFile):
    default_ext = file_formats.ZIM
    allowed_formats = [file_formats.ZIM]
    is_primary = True

    def get_preset(self):
        return self.preset or format_presets.ZIM


class ZimNode(nodes.ContentNode):
    """
    Zim content node. Accepts ZimFile as a type of file.
    """

    kind = content_kinds.ZIM
    required_file_format = file_formats.ZIM

    def get_thumbnail_preset(self):
        """
        Returns the format preset corresponding to this Node's type,
        or None if the node doesn't have a format preset.
        """
        return format_presets.ZIM_THUMBNAIL

    def generate_thumbnail(self):
        # TODO: Generate Zim file thumbnail here?
        return None

    def validate(self):
        """validate: Makes sure document node contains at least one EPUB or PDF
        Args: None
        Returns: boolean indicating if document is valid
        """
        try:
            assert self.kind == content_kinds.ZIM, "Assumption Failed: Node should be zim"
            assert self.questions == [], "Assumption Failed: Zim should not have questions"
            assert len(self.files) > 0, "Assumption Failed: Zim should have at least one file"
            assert [f for f in self.files if isinstance(f, ZimFile)], "Assumption Failed: Zim should have at least one zim file"
            return super(ZimNode, self).validate()
        except AssertionError as ae:
            raise InvalidNodeException("Invalid node ({}): {} - {}".format(ae.args[0], self.title, self.__dict__))


if __name__ == "__main__":
    chef = EncyclopediaChef()
    chef.main()
