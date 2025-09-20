materialTables:
  tables:
  - header: '## Physical Properties'
    rows:
    - property: Density
      value: '7.85'
      unit: "g/cm\xB3"
      min: '1.8'
      max: '6.0'
      percentile: 51.2
      htmlVisualization: '<div class="w-full bg-gray-200 rounded-full h-2"><div class="bg-blue-600
        h-2 rounded-full" style="width: 100%"></div></div><p class="text-xs text-center">Value
        at 100% of range</p>'
    - property: Melting Point
      value: '1450.0'
      unit: "\xB0C"
      percentile: 54.5
      htmlVisualization: <span class="text-gray-500">-</span>
  - header: '## Thermal Properties'
    rows:
    - property: Thermal Conductivity
      value: '50.2'
      unit: "W/m\xB7K"
      percentile: 14.8
      htmlVisualization: <span class="text-gray-500">-</span>
  - header: '## Mechanical Properties'
    rows:
    - property: Tensile Strength
      value: '500.0'
      unit: MPa
      percentile: 26.3
      htmlVisualization: <span class="text-gray-500">-</span>
    - property: Hardness
      value: '200.0'
      unit: HB
      min: '500.0'
      max: '2500.0'
      percentile: 0.0
      htmlVisualization: '<div class="w-full bg-gray-200 rounded-full h-2"><div class="bg-blue-600
        h-2 rounded-full" style="width: 0%"></div></div><p class="text-xs text-center">Value
        at 0% of range</p>'
    - property: Young's Modulus
      value: '200.0'
      unit: GPa
      min: '150.0'
      max: '400.0'
      percentile: 92.0
      htmlVisualization: '<div class="w-full bg-gray-200 rounded-full h-2"><div class="bg-blue-600
        h-2 rounded-full" style="width: 20%"></div></div><p class="text-xs text-center">Value
        at 20% of range</p>'
  - header: '## Laser Processing Parameters'
    rows:
    - property: Laser Type
      value: Pulsed Fiber Laser
      unit: '-'
      htmlVisualization: <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded">Standard</span>
    - property: Wavelength
      value: 1064nm
      unit: nm
      htmlVisualization: <span class="px-2 py-1 bg-green-100 text-green-800 rounded">Optimal</span>
    - property: Fluence Range
      value: "1.0\u20134.5 J/cm\xB2"
      unit: "J/cm\xB2"
      htmlVisualization: '<div class="w-full bg-gray-200 rounded-full h-2"><div class="bg-orange-600
        h-2 rounded-full" style="width: 75%"></div></div>'
  - header: '## Composition'
    rows:
    - property: Chemical Formula
      value: Fe
      unit: '-'
      htmlVisualization: <span class="font-mono text-sm bg-gray-100 px-2 py-1 rounded">Chemical</span>
renderInstructions: 'In Next.js, loop over tables[].rows and render as <table> with
  <tr><td>{property}</td><td>{value} ({unit})</td><td>{min}-{max}</td><td>{percentile
  ? percentile + ''%'' : ''N/A''}</td><td dangerouslySetInnerHTML={{__html: htmlVisualization}}
  /></tr>. Use MDX for headers.'


---
Version Log - Generated: 2025-09-19T16:58:46.597019
Material: Aluminum
Component: table
Generator: Z-Beam v2.1.0
Author: AI Assistant
Platform: Darwin (3.12.4)
File: content/components/table/aluminum-laser-cleaning.md
---