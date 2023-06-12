import requests
import svgwrite
from PIL import Image
import io
import json
def take_inputs():
    global name
    global description
    global url
    global service

    name = input("Enter API name: ")
    mdname = name.replace(' ', '-')
    oname = name.replace(' ', '_')
    description = input("Enter API description: ")
    url = input("Enter API URL: ")
    print("Choose the type:")
    print("1. Marketing")
    print("2. HumanResources")
    print("3. Finance")
    print("4. Productivity")
    print("5. Engineering")
    print("6. Support")
    print("7. Sales")
    print("8. Security")
    print("9. BITool")
    service = int(input("Enter the choice number: "))
try:
    file_location = input("Enter the file location: ")

    with open(file_location, 'r') as file:
        json_data = json.load(file)

        name = json_data["name"]
        mdname = name.replace(' ', '-')
        oname = name.replace(' ', '_')
        description= json_data["description"]
        url = json_data["url"]

        service = json_data["service"]


        if not any([name, description, url, service]):
            take_inputs()

except FileNotFoundError:
    take_inputs()

def generate_setup_guide(mdname, oname):
    setup_guide = (
        f"# {cap(name)} Setup Guide {{{{ typeBadge \"{oname.lower()}\" }}}} {{{{ availabilityBadge \"{oname.lower()}\" }}}}\n"
        f"\n"
        f"Follow our setup guide to connect {cap(name)} to Fivetran.\n"
        f"\n"
        f"------\n"
        f"\n"
        f"## Prerequisites\n"
        f"\n"
        f"To connect {cap(name)} to Fivetran, you need a [{cap(name)}]({url}) account.\n"
        f"\n"
        f"------\n"
        f"\n"
        f"## Setup instructions\n"
        f"\n"
        f"### <span class=\"step-item\">Heading</span>\n"
        f"Write Steps here\n"
        f"> Note : \n"
        f"\n"
        f"### <span class=\"step-item\">Finish Fivetran configuration </span>\n"
        f"\n"
        f"Steps here\n"
        f"\n"
        f"-----\n"
        f"\n"
        f"## Related articles\n"
        f"\n"
        f"[<i aria-hidden=\"true\" class=\"material-icons\">description</i> Connector Overview](/docs/applications/{mdname})\n"
        f"\n"
        f"<b> </b>\n"
        f"\n"
        f"[<i aria-hidden=\"true\" class=\"material-icons\">home</i> Documentation Home](/docs/getting-started)\n"
    )
    with open(f"{mdname.lower()}-setup-guide.md", "w") as f:
        f.write(setup_guide)

def cap(sentence):
    words = sentence.split()
    capitalized_words = [word.capitalize() for word in words]
    capitalized_sentence = ' '.join(capitalized_words)
    return capitalized_sentence


def ico_to_svg(ico_data):
    # Open ICO data
    ico_image = Image.open(ico_data)

    # Get the size of the ICO image
    width, height = ico_image.size

    # Create a new SVG drawing
    dwg = svgwrite.Drawing()

    # Set the size of the SVG canvas
    dwg['width'] = f"{width}px"
    dwg['height'] = f"{height}px"

    # Iterate over each pixel in the ICO image and set the corresponding SVG pixel
    for y in range(height):
        for x in range(width):
            pixel = ico_image.getpixel((x, y))
            dwg.add(dwg.rect(insert=(x, y), size=(1, 1), fill=f"rgb{pixel[:3]}"))

    # Return the SVG code
    return dwg.tostring()


def generate_files(name, description, url, mdname, oname):
    name_md = (
        f"# {cap(name)} {{{{ typeBadge \"{oname.lower()}\" }}}} {{{{ availabilityBadge \"{oname.lower()}\" }}}}\n"
        f"\n"
        f"[{cap(name)}]({url}) {description}\n\n"
        f"-----\n"
        f"\n"
        f"## Features\n"
        f"\n"
        f"{{{{#featureTable \"{oname.lower()}\"}}}}\n"
        f"Capture Deletes: All tables\n"
        f"Column Hashing:\n"
        f"Data Blocking: Column level\n"
        f"Re-sync: Connector level\n"
        "{{/featureTable}}\n"
        f"\n"
        f"-----\n"
        f"\n\n"
        f"## Setup guide\n"
        f"\n"
        f"Follow our [step-by-step {cap(name)} setup guide](/docs/applications/{mdname.lower()}/setup-guide) to connect {cap(name)} with your destination using Fivetran connectors.\n"
    )
    with open(f"{mdname.lower()}.md", "w") as f:
        f.write(name_md)

    type_mapping = {
        1: "Marketing",
        2: "HumanResources",
        3: "Finance",
        4: "Productivity",
        5: "Engineering",
        6: "Support",
        7: "Sales",
        8: "Security",
        9: "BITool"
    }

    ss = type_mapping.get(service, "")
    name_config_yaml = f"""---
service:
  name: "{cap(name)}"
  description: "{description}"
  docsPath: "/docs/applications/{mdname.lower()}"
  logo: "/integrations/coil_connectors/resources/{oname.lower()}/resources/{oname.lower()}.svg"
  availability: "development"
  connectorType: "lite"
  type: "{ss}"
  languageVersion: "2.0.0"
api: {{}}
metrics: {{}}
"""
    with open(f"{oname.lower()}.config.yaml", "w") as f:
        f.write(name_config_yaml)

    name_yaml = f"""    - name: {cap(name)}
      hidden: true
      file: {mdname.lower()}.md
      path: /docs/applications/{mdname.lower()}
      title: {cap(name)} connector by Fivetran | Fivetran documentation
      description: Connect your {cap(name)} data to your destination using Fivetran. Learn about configuration requirements, setup, and ERDs with our technical documentation.
      children:
        - name: Setup Guide
          hidden: true
          file: {mdname.lower()}-setup-guide.md
          path: /docs/applications/{mdname.lower()}/setup-guide
          title: {cap(name)} data connector by Fivetran | Setup Guide
          description: Read step-by-step instructions on how to connect {cap(name)} with your destination using Fivetran connectors."""
    with open(f"{oname.lower()}.yaml", "w") as f:
        f.write(name_yaml)

    response = requests.get(url)
    html_content = response.text

    favicon_url = None
    link_tags = html_content.split('<link ')
    for link_tag in link_tags:
        if 'rel="shortcut icon"' in link_tag or 'rel="icon"' in link_tag or 'rel="apple-touch-icon"' in link_tag:
            href_index = link_tag.find('href=')
            if href_index != -1:
                url_start = link_tag.find('"', href_index)
                url_end = link_tag.find('"', url_start + 1)
                favicon_url = link_tag[url_start + 1:url_end]
                break

    if favicon_url:
        if not favicon_url.startswith('http'):
            favicon_url = url.rstrip('/') + favicon_url


        link_tags = html_content.split('<link ')
        response = requests.get(favicon_url)
        favicon_data = response.content

        # Check if the favicon is in ICO format
        if response.headers.get('content-type') == 'image/x-icon':
            # Convert ICO to SVG
            svg_code = ico_to_svg(io.BytesIO(favicon_data))

            # Save the SVG code to a file
            with open(f"{oname.lower()}.svg", "w") as file:
                file.write(svg_code)

            print(f"SVG code saved as {name.lower()}.svg")
        else:
            try:
                # Check if the favicon is in PNG format
                favicon_image = Image.open(io.BytesIO(favicon_data))
                # Convert PNG to ICO
                ico_data = io.BytesIO()
                favicon_image.save(ico_data, format='ICO')
                ico_data.seek(0)

                # Convert ICO to SVG
                svg_code = ico_to_svg(ico_data)

                # Save the SVG code to a file
                with open(f"{oname.lower()}.svg", "w") as file:
                    file.write(svg_code)

                print(f"SVG code saved as {name.lower()}.svg")
            except:
                print("Favicon is neither in ICO nor PNG format.")
    else:
        print("No favicon found.")




print("Shashank Industries Production")
generate_setup_guide(mdname, oname)
generate_files(name, description, url, mdname, oname)

