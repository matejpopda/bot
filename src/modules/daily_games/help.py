from ...modules import response_utils 
from discord.ext import pages



help_page_groups = []

footer="Navigate using this dropdown!"
text="This module is used for plotting statistics of different available daily games.\n\n\n " \
"The related dailies-debug slash commands are used to setup the bot. (Available only for people with manage channels permissions.)"
front_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title="Dailies module introduction", footer=footer)])
help_page_groups.append(pages.PageGroup([front_page], "Introduction"))



title = "The game_info command"
text = "Use this command to find information about available games."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))

title = "The help command"
text = "Displays this menu."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))

title = "The multi_graph command"
text = "Plot a graph for up to 4 different users."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))

title = "The user_graph command"
text = "Plot a graph for one particular users. Has more options than the multi_graph command."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))

title = "The dailies-debug channel-ingestion command"
text = "For users with manage channel permissions. \n Allows you to save or forget all scores that the bot saved in its memory."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))



title = "The dailies-debug channel-registration command"
text = "For users with manage channel permissions. \n Allows you to register a channel. The bot will then automatically save scores that get posted in the channel. " \
"Furthermore for some specific games the bot will occasionally post a direct link for convenience."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))



def get_help_paginator():


    paginator = pages.Paginator(pages=help_page_groups, show_menu=True, show_disabled=False, show_indicator=False)
    return paginator