const fs = require('fs');
const yaml = require('js-yaml');
const YAML = require('json-to-pretty-yaml');
const { type } = require('os');
const { title } = require('process');

// How to use:
// node bs2ops <filename>

// Example yml (catalog-info.yml) is also provided to test function:
// node bs2ops example-input.yml
//  Expected output:
// Writing artist-web service info to opslevel-artist-web.yml...
// Writing extra data to leftoverBSdata-artist-web.json...

// Backstage (BS) info is mapped to OpsLevel yml attributes
// The extra BS info is written to another file for future reference

// OpsLevel yml file documentation
// https://www.opslevel.com/docs/opslevel-yml#example-service-opslevelyml

const mapFile = (filePath) => {
  const tempJSON = {
    "version": 1,
    "service": {}
  };

  if (!fs.existsSync(filePath)) {
    console.log(`\n${filePath} does not exist, exiting....\n`)
    process.exit(1);
  }

  const fileContents = fs.readFileSync(filePath, 'utf8');
  const data = yaml.load(fileContents)

  if (!("metadata" in data)) {
    console.log("\nProperties for this service are missing, exiting ...\n")
    process.exit(1);
  }

  if (!data.metadata.name) {
    console.log("\nProperties for this service is missing the service name, exiting ...\n")
    process.exit(1);
  }

  const mappings = [
    {
      source: data => data.metadata.name,
      mapping: source => { tempJSON.service.name = source }
    },
    {
      source: data => data.spec.lifecycle,
      mapping: source => { tempJSON.service.lifecycle = source }
    },
    {
      source: data => data.spec.system,
      mapping: source => { tempJSON.service.product = source }
    }, {
      source: data => data.spec.owner,
      mapping: source => { tempJSON.service.owner = source }
    }, {
      source: data => data.metadata.description,
      mapping: source => { tempJSON.service.description = source }
    }, {
      source: data => data.metadata.tags,
      mapping: source => {
        tempJSON.service.tags = source.map(tag => ({ key: "tag", value: tag }))
      }
    }, {
      source: data => data.metadata.links,
      mapping: source => {
        tempJSON.service.tools = source.map(link => ({ name: link.title, category: link.icon, url: link.url }))
      },
    }
  ]

  mappings.forEach(({ source, mapping }) => {
    if (source(data)) {
      mapping(source(data))
    }
  })

  const js_filename = `opslevel-${data.metadata.name}.yml`
  const json_filename = `leftoverBSdata-${data.metadata.name}.json`

  const yamlOutput = YAML.stringify(tempJSON)
  fs.writeFileSync(js_filename, yamlOutput)

  console.log(`\nWriting ${data.metadata.name} service info to ${js_filename}...`)

  //  this is the data from the BS yml file that was not 
  //  added to the opslevel.yml file
  leftoverData = {
    "api": data.apiVersion,
    "kind": data.kind,
    "labels": data.metadata.labels,
    "annotations": data.metadata.annotations
  }

  fs.writeFileSync(json_filename, JSON.stringify(leftoverData, null, 2), "utf8")
  console.log(`Writing extra data to ${json_filename}...`)
}

const filePaths = process.argv.slice(2);

if (!filePaths.length) {
  console.log('\nMISSING path to the file');
  console.log('Usage: node bs2ops.js <file paths>');
  console.log('Example: node bs2ops.js first.yml another.yml\n')
  return
}

for (const filePath of filePaths) {
  mapFile(filePath)
}

  console.log(`%c
                \/\\___\/\\
               {>^ . ^<}
                [  _  ]         
               [["] ["]]_/

        **** Sir Ops-a-lot ****
        *****   Says Hi   *****
                         `, "font-family:monospace");


