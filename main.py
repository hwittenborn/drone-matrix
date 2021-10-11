#!/usr/bin/env python3
import asyncio
import logging
import nio
import os
import re

from markdown import markdown
from textwrap import dedent

env = os.environ
logging.basicConfig(level=logging.INFO)

# Make sure needed arguments are set.
missing_env_vars = False

for i in ["USERNAME", "HOMESERVER", "PASSWORD", "ROOM"]:
    if env.get(f"PLUGIN_{i}") is None:
        logging.error(f"{i} isn't set")
        missing_env_vars = True

for i in ["DRONE_REPO", "DRONE_BRANCH", "DRONE_COMMIT_SHA", "DRONE_COMMIT_LINK",
          "DRONE_STAGE_STATUS", "DRONE_SYSTEM_PROTO", "DRONE_SYSTEM_HOST", "DRONE_BUILD_NUMBER"]:
    if env.get(i) is None:
        logging.error(f"{i} isn't set")
        missing_env_vars = True

if missing_env_vars == True:
    exit(1)

# Set environment variables.
conf_username = env["PLUGIN_USERNAME"]
conf_password = env["PLUGIN_PASSWORD"]
conf_homeserver = env["PLUGIN_HOMESERVER"]
conf_room = env["PLUGIN_ROOM"]

conf_drone_repo = env["DRONE_REPO"]
conf_drone_branch = env["DRONE_BRANCH"]
conf_drone_commit_sha = env["DRONE_COMMIT_SHA"]
conf_drone_commit_link = env["DRONE_COMMIT_LINK"]
conf_drone_stage_status = env["DRONE_STAGE_STATUS"]

conf_drone_system_proto = env["DRONE_SYSTEM_PROTO"]
conf_drone_system_host = env["DRONE_SYSTEM_HOST"]
conf_drone_build_number = env["DRONE_BUILD_NUMBER"]

# Start actually doing stuff.
async def main():
    client = nio.AsyncClient(conf_homeserver, conf_username)
    login = await client.login(conf_password)

    # Log in.
    try:
        login.status_code
        logging.error("Invalid authentication credentials were provided.")
        await client.close()
        exit(1)
    except AttributeError:
        logging.info("Succesfully logged in.")

    # Make sure any room specified is valid an mapped to an actual room ID.
    if conf_room[0] == "#":
        room_id = (await client.room_resolve_alias(conf_room)).room_id
    elif conf_room[0] == "!":
        room_id = conf_room
    else:
        logging.error(f"Invalid room specified: '{conf_room}'.")
        await client.close()
        exit(1)

    # Prepare the message.
    if conf_drone_stage_status == "success":
        build_status_message = "success"
        build_status_icon = "🟢"
    elif conf_drone_stage_status == "failure":
        build_status_message = "failure"
        build_status_icon = "🔴"
    else:
        logging.warning(f"Unknown build status '{conf_drone_stage_status}'.")
        build_status_message = f"unknown"
        build_status_icon = "⚪️"

    message = f"""
               **{conf_drone_repo}** [#{conf_drone_build_number}]({conf_drone_system_proto}://{conf_drone_system_host}/{conf_drone_repo}/{conf_drone_build_number})   
               Branch: {conf_drone_branch}   
               Commit: [{conf_drone_commit_sha}]({conf_drone_commit_link})   
               Status: {build_status_message} {build_status_icon}
               """

    message = dedent(message)
    message = re.sub("^\n|\n$", "", message)

    formatted_message = markdown(message)

    body = {
        "msgtype": "m.text",
        "body": message,
        "format": "org.matrix.custom.html",
        "formatted_body": formatted_message
    }

    # Send the message.
    logging.info(f"Sending build notification to '{conf_room}'...")
    await client.room_send(room_id=room_id,
                           message_type="m.room.message",
                           content=body)
    
    # Log out.
    logging.info("Logging out...")
    await client.logout()
    
    await client.close()

asyncio.run(main())
