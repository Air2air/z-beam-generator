import yaml

data = yaml.safe_load(open('data/Materials.yaml'))
mats = data.get('materials', {})
al = mats.get('Aluminum', {})

print(f"Aluminum keys: {list(al.keys())}")
print(f"Has faq: {'faq' in al}")

faq = al.get('faq')
print(f"FAQ type: {type(faq)}")

if isinstance(faq, list):
    print(f"FAQ has {len(faq)} questions")
    print(f"First question: {faq[0]['question'][:80]}...")
    print(f"Answer preview: {faq[0]['answer'][:150]}...")
elif isinstance(faq, dict):
    print(f"FAQ has {len(faq)} questions")
    q1_key = list(faq.keys())[0]
    print(f"First question: {q1_key[:80]}...")
    print(f"Answer preview: {faq[q1_key]['answer'][:150]}...")
