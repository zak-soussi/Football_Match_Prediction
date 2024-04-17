def generate_commands():
    commands = []
    for year in range(2017, 2024):
        season = f"{year}-{year+1}"
        country = "france"
        league = f"ligue-2-{season.replace('-', '-')}"
        path = f"./src/data/json/{country}"
        command = f"npm run start country={country} league={league} path={path} headless"
        commands.append(command)
    return commands

commands_list = generate_commands()
#save commands to a file
with open("commands.txt", "w") as file:
    for command in commands_list:
        file.write(f"{command}\n")

