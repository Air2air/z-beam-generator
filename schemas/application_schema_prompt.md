```yaml
schemaVersion: "1.0"
schemaType: "LaserCleaningApplicationProfile"
applicationProfile:

# Core application information

applicationName: "{{applicationName}}" # Placeholder for dynamic application name
description:
type: string
description: "Overview of the laser cleaning application"
example: "{{applicationName}} uses high-energy laser pulses to remove coatings, preserving substrates like steel and aluminum for refurbishment in manufacturing."
primaryAudience:
type: string
description: "Primary target audience for the application"
example: "Industrial Engineers"
secondaryAudience:
type: string
description: "Secondary target audience for the application"
example: "Production Managers"
industries:
type: array
items:
type: string
description: "Industries where the application is commonly used"
example: ["Automotive", "Furniture Manufacturing"]
substrates:
type: array
items:
type: string
description: "Substrates commonly cleaned in this application"
example: ["Steel", "Aluminum"]

# Laser cleaning parameters

laserParameters:
type: object
properties:
description:
type: string
description: "Overview of laser parameters for the application"
example: "Optimized parameters for {{applicationName}} ensure efficient coating removal while preserving substrate integrity."
parameters:
type: array
items:
type: object
properties:
name:
type: string
description: "Name of the parameter"
example: "Scan Speed"
unit:
type: string
description: "Unit of measurement"
example: "mm/s"
optimalRange:
type: string
description: "Optimal range for the parameter"
example: "1100–1400"
fullRanges:
type: array
items:
type: string
description: "Full range of parameter values"
example: ["500–800", "800–1100", "1100–1400", "1400–1700", "1700–2000", "2000–2300", "2300–2600", "2600–2900"]
example: - name: "Scan Speed"
unit: "mm/s"
optimalRange: "1100–1400"
fullRanges: ["500–800", "800–1100", "1100–1400", "1400–1700", "1700–2000", "2000–2300", "2300–2600", "2600–2900"] - name: "Fluence"
unit: "J/cm²"
optimalRange: "2.2–2.6"
fullRanges: ["1.4–1.8", "1.8–2.2", "2.2–2.6", "2.6–3.0", "3.0–3.4", "3.4–3.8", "3.8–4.2", "4.2–4.6"] - name: "Pulse Duration"
unit: "ns"
optimalRange: "40–50"
fullRanges: ["20–30", "30–40", "40–50", "50–60", "60–70", "70–80", "80–90", "90–100"] - name: "Power Output"
unit: "W"
optimalRange: "200–240"
fullRanges: ["120–160", "160–200", "200–240", "240–280", "280–320", "320–360", "360–400", "400–440"]
dataSource:
type: string
description: "Source of parameter data"
example: "Optics & Laser Technology, 2023"

# Successful cleaning outcomes

outcomes:
type: array
items:
type: object
properties:
outcome:
type: string
description: "Name of the outcome"
example: "Substrate Preservation"
description:
type: string
description: "Description of the outcome"
example: "Removes coatings without damaging substrates, enabling recoating in {{applicationName}}."
example: - outcome: "Substrate Preservation"
description: "Removes coatings without damaging substrates, enabling recoating in {{applicationName}}." - outcome: "High Efficiency"
description: "Achieves rapid removal rates, streamlining refurbishment processes." - outcome: "Environmental Benefits"
description: "Eliminates chemical strippers, reducing hazardous waste."

# Challenges

challenges:
type: array
items:
type: object
properties:
challenge:
type: string
description: "Name of the challenge"
example: "Parameter Sensitivity"
description:
type: string
description: "Description of the challenge"
example: "Incorrect parameter settings may leave residues or affect substrate finish in {{applicationName}}."
example: - challenge: "Parameter Sensitivity"
description: "Incorrect parameter settings may leave residues or affect substrate finish in {{applicationName}}." - challenge: "Equipment Costs"
description: "High initial investment for laser systems, though offset by reduced material costs." - challenge: "Operator Expertise"
description: "Requires trained operators to adjust settings for varying coating thicknesses."

# Performance metrics

performanceMetrics:
type: object
properties:
description:
type: string
description: "Overview of performance metrics for the application"
example: "Performance metrics for {{applicationName}} ensure high-throughput refurbishment with minimal substrate damage."
metrics:
type: array
items:
type: object
properties:
name:
type: string
description: "Name of the metric"
example: "Cycle Time"
unit:
type: string
description: "Unit of measurement"
example: "s/cm²"
optimalRange:
type: string
description: "Optimal range for the metric"
example: "0.09–0.18"
fullRanges:
type: array
items:
type: string
description: "Full range of metric values"
example: ["0.09–0.18", "0.18–0.27", "0.27–0.36", "0.36–0.45", "0.45–0.54", "0.54–0.63", "0.63–0.72", "0.72–0.81"]
example: - name: "Cycle Time"
unit: "s/cm²"
optimalRange: "0.09–0.18"
fullRanges: ["0.09–0.18", "0.18–0.27", "0.27–0.36", "0.36–0.45", "0.45–0.54", "0.54–0.63", "0.63–0.72", "0.72–0.81"] - name: "Surface Roughness"
unit: "µm"
optimalRange: "0.2–0.4"
fullRanges: ["0.2–0.4", "0.4–0.6", "0.6–0.8", "0.8–1.0", "1.0–1.2", "1.2–1.4", "1.4–1.6", "1.6–1.8"] - name: "Energy Consumption"
unit: "kWh/m²"
optimalRange: "0.7–1.1"
fullRanges: ["0.7–1.1", "1.1–1.5", "1.5–1.9", "1.9–2.3", "2.3–2.7", "2.7–3.1", "3.1–3.5", "3.5–3.9"] - name: "Cleaning Efficiency"
unit: "%"
optimalRange: "95–100"
fullRanges: ["80–85", "85–90", "90–95", "95–100", "100–105", "105–110", "110–115", "115–120"]
dataSource:
type: string
description: "Source of performance metrics"
example: "Materials Today: Proceedings, 2023"

# Cleaning speed comparison

cleaningSpeedComparison:
type: object
properties:
description:
type: string
description: "Overview of cleaning speed comparison"
example: "Laser cleaning for {{applicationName}} outperforms traditional methods in speed and precision."
methods:
type: array
items:
type: object
properties:
method:
type: string
description: "Cleaning method"
example: "Laser Cleaning"
speed:
type: string
description: "Cleaning speed range"
example: "0.09–0.18 s/cm²"
example: - method: "Laser Cleaning"
speed: "0.09–0.18 s/cm²" - method: "Sandblasting"
speed: "0.6–1.2 s/cm²" - method: "Chemical Stripping"
speed: "0.8–1.5 s/cm²" - method: "Manual Cleaning"
speed: "1.0–2.0 s/cm²"
chartConfig:
type: object
properties:
type:
type: string
description: "Type of chart for visualization"
example: "bar"
dataSource:
type: string
description: "Source of speed comparison data"
example: "Journal of Laser Applications, 2024"
example:
type: "bar"
dataSource: "Journal of Laser Applications, 2024"

# Cost comparison

costComparison:
type: object
properties:
description:
type: string
description: "Overview of cost comparison for cleaning methods"
example: "Laser cleaning for {{applicationName}} offers lower operational costs compared to traditional methods."
methods:
type: array
items:
type: object
properties:
method:
type: string
description: "Cleaning method"
example: "Laser Cleaning"
cost:
type: string
description: "Cost range in USD per square meter"
example: "$10–20/m²"
example: - method: "Laser Cleaning"
cost: "$10–20/m²" - method: "Sandblasting"
cost: "$25–45/m²" - method: "Chemical Stripping"
cost: "$20–35/m²" - method: "Manual Cleaning"
cost: "$30–50/m²"
chartConfig:
type: object
properties:
type:
type: string
description: "Type of chart for visualization"
example: "bar"
dataSource:
type: string
description: "Source of cost data"
example: "Surface and Coatings Technology, 2022"
example:
type: "bar"
dataSource: "Surface and Coatings Technology, 2022"

# Safety and regulatory considerations

safetyConsiderations:
type: array
items:
type: string
description: "Safety requirements for the application"
example: - "Mandatory laser-safe goggles for operators" - "Ventilation systems to manage vaporized coatings" - "Operator training for parameter optimization"

regulatoryStandards:
type: array
items:
type: string
description: "Industry standards and regulations applicable to the application"
example: ["OSHA 1910.147", "ANSI Z136.1", "EPA Hazardous Waste Regulations"]

# Author information

author:
type: object
properties:
authorId:
type: string
description: "Unique identifier for the author"
example: "4"
authorName:
type: string
description: "Full name of the author"
example: "Ikmanda Roswati"
authorTitle:
type: string
description: "Professional title of the author"
example: "Laser Cleaning Expert"
authorCountry:
type: string
description: "Country of the author"
example: "Indonesia"
authorImage:
type: string
description: "URL of the author's image"
example: "/images/authors/ikmanda-roswati.jpg"
authorSlug:
type: string
description: "Slug for the author's profile page"
example: "ikmanda-roswati"

# Content management information

contentManagement:
type: object
properties:
articleType:
type: string
description: "Type of article"
example: "application-profile"
publishedAt:
type: string
format: date
description: "Publication date"
example: "2025-07-10"
lastUpdated:
type: string
format: date
description: "Last update date"
example: "2025-07-10"
generationTimestamp:
type: string
format: date-time
description: "Timestamp of content generation"
example: "2025-07-10T20:11:12.721302Z"
modelUsed:
type: string
description: "Model used for content generation"
example: "Grok3"

# Related content

relatedContent:
type: array
items:
type: object
properties:
title:
type: string
description: "Title of related content"
example: "Laser Cleaning in Automotive Manufacturing"
url:
type: string
description: "URL of related content"
example: "https://example.com/articles/laser-cleaning-automotive"
type:
type: string
description: "Type of related content"
example: "article"
```
