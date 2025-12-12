from ...modules import response_utils 
from discord.ext import pages



help_page_groups = []

footer="Navigate using the dropdown below!"
text="This module is used for plotting statistics of different available daily games.\n\n\n " \
"The related dailies-debug slash commands are used to setup the bot. (Available only for people with manage channels permissions.)"
front_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title="Dailies module introduction", footer=footer)])
help_page_groups.append(pages.PageGroup([front_page], "Introduction"))

title = "/dailies help"
text = "Displays this menu."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))

title = "/dailies most_recent_games"
text = "This command prints out a table of latest scores from games played in the last 3 days.\n " \
"The ✅ ⛔ marks if a game was played today or not.\n" \
"The verbose option prints out even older games, furhermore it also displays when they were played and score. "
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))

title = "/dailies game_info"
text = "Use this command to find information about available games."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))


title = "/dailies user_stats"
text = "Returns the raw stats for a user in one game. You can select which format you require."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))

title = "/dailies multi_graph"
text = "Plot a graph for up to 4 different users."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))

title = "/dailies user_graph"
text = "Plot a graph for one particular users. Has more options than the multi_graph command."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))

title = "/dailies-debug channel_ingestion"
text = "For users with manage channel permissions. \n Allows you to save or forget all scores that the bot saved in its memory."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))



title = "/dailies-debug channel_registration"
text = "For users with manage channel permissions. \n Allows you to register a channel. The bot will then automatically save scores that get posted in the channel. " \
"Furthermore for some specific games the bot will occasionally post a direct link for convenience."
info_page = pages.Page(
    embeds = [response_utils.string_to_pages_embed(text=text, title=title)])
help_page_groups.append(pages.PageGroup([info_page],title))



def get_help_paginator():


    paginator = pages.Paginator(pages=help_page_groups, show_menu=True, show_disabled=False, show_indicator=False)

    original_on_timeout = paginator.on_timeout
    async def on_timeout_overload():
        await original_on_timeout()

        assert paginator.message is not None

        await paginator.message.edit(view=None)

    
    paginator.on_timeout = on_timeout_overload
    return paginator