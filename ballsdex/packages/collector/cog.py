import logging
import json

import discord
from discord import app_commands
from discord.ext import commands

from typing import TYPE_CHECKING, Optional, cast

from ballsdex.core.models import BallInstance
from ballsdex.core.models import Player
from ballsdex.core.utils.transformers import BallEnabledTransform
from ballsdex.core.utils.transformers import SpecialTransform
from ballsdex.settings import settings

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot

log = logging.getLogger("ballsdex.packages.collector.cog")

# HOW TO USE THIS PACKAGE.
# STEP 1:
# CREATE A JSON FILE NAMED "collector.json".
# WRITE THE DATA IN THE FOLLOWING FORMAT.
# {"ITEM_1" : NUMBER_OF_INSTANCES_NEEDED_TO_GET_COLLECTOR_FOR_THIS_ITEM ,  "ITEM_2" : NUMBER_OF_INSTANCES_NEEDED_TO_GET_COLLECTOR_FOR_THIS_ITEM}
# FOR EXAMPLE:
# {"China" : 100, "Japan" : 50, "India" : 30}
# STEP 2:
# CREATE A SPECIAL EVENT NAMED "collector".
# SET THE DATES SUCH THAT THE EVENT ENDS EVEN BEFORE IT IS CREATED.
# FOR EXAMPLE:
# IF YOU ARE MAKING THE EVENT ON 1ST JULY 2024,
# SET THE END DATE OF THE EVENT ON 30TH JUNE 2024 OR EARLIER.
# STEP 3:
# CHECK IF IT WORKS AND ENSURE THAT IT DOES.
# THAT'S ALL 

class Collector(commands.GroupCog):
    """
    Collector commands.
    """

    def __init__(self, bot: "BallsDexBot"):
        self.bot = bot
    
    @app_commands.command()
    async def card(
        self,
        interaction: discord.Interaction,
        countryball: BallEnabledTransform,
        ):
        """
        Get the collector card for a countryball.

        Parameters
        ----------
        countryball: Ball
            The countryball you want to obtain the collector card for.
        """
          
        if interaction.response.is_done():
            return
        assert interaction.guild
        filters = {}
        if countryball:
            filters["ball"] = countryball
        await interaction.response.defer(ephemeral=True, thinking=True)
        filters["player__discord_id"] = interaction.user.id
        balls = await BallInstance.filter(**filters).count()
        with open("collector.json", "r") as f:
            collector_json = json.load(f)
        collector_number = collector_json[countryball.country]
        country = f"{countryball.country}"
        player, created = await Player.get_or_create(discord_id=interaction.user.id)
        if balls >= collector_number:
            await interaction.followup.send(
                f"Congrats! You are now a {country} collector.", 
                ephemeral=True
            )
            await BallInstance.create(
            ball=countryball,
            player=player,
            attack_bonus=0,
            health_bonus=0,
            special=collector,
            )
        else:
            await interaction.followup.send(
                f"You need {collector_number - balls} more {country} {settings.collectible_name} to be eligible for collector."
            )
          
