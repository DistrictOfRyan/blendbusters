#!/usr/bin/env python3
"""ONE definition of who writes BlendBusters. (2026-09-08)

Until today every page credited "the BlendBusters desk" (217 pages) or "the
BlendBusters editorial team" (about.html), and Article.author in the JSON-LD
pointed at the Organization. An anonymous desk asking a reader to trust its
arithmetic over a brand's is the weakest authority position available, it is a
straight E-E-A-T deficiency on a supplements topic, and an answer engine has no
person to attribute a citation to.

HONESTY BOUNDARY, deliberate and load-bearing: the credential below claims
software, analytics and methodology work, and nothing else. William Ryan Hunt is
not a clinician, a dietitian, a nutritionist or a medical reviewer, and no line
here may imply otherwise. What he actually did is build the price-comparison
method and the data pipeline, which is exactly the expertise this site's claims
rest on. Every fact below is from his real record:

  BS Computer Science, University of Kentucky (minors: Mathematical Science, Business)
  MBA, Johns Hopkins Carey Business School (Finance, Marketing, Entrepreneurial Leadership)
  15+ years building software, web platforms and web analytics
  linkedin.com/in/DistrictOfRyan

Nothing in this module is a nutrition, medical or dietetics credential. Do not add one.
"""

SITE = 'https://blendbusters.com'

NAME = 'William Ryan Hunt'
AUTHOR_ID = SITE + '/about#author'
ROLE = 'Founder and data lead, BlendBusters'

# One-line credential for a visible byline. No health expertise claimed.
CREDENTIAL = ('built the BlendBusters price-comparison method and the data pipeline behind '
              'every page on this site')

# Longer version for about.html and for schema descriptions.
BIO = ('William Ryan Hunt built the BlendBusters price-comparison method and the data pipeline '
       'that produces every comparison on this site. He holds a BS in Computer Science from the '
       'University of Kentucky and an MBA from the Johns Hopkins Carey Business School, and has '
       'spent more than fifteen years building software, web platforms and web analytics. He is '
       'not a clinician, a dietitian or a nutritionist, and BlendBusters makes no medical claims: '
       'what this site does is read labels, normalize doses to a comparable monthly cost, and '
       'show the arithmetic so you can check it.')

# Same bio without the leading name, for a visible byline that already names him.
BIO_NO_NAME = BIO.replace('William Ryan Hunt built', 'He built', 1)

LINKEDIN = 'https://www.linkedin.com/in/DistrictOfRyan'


def person_ld(full=False):
    """The author as a schema.org Person. Use as Article.author / Dataset.creator."""
    if not full:
        return {'@id': AUTHOR_ID}
    return {
        '@type': 'Person',
        '@id': AUTHOR_ID,
        'name': NAME,
        'url': SITE + '/about',
        'jobTitle': ROLE,
        'description': BIO,
        'sameAs': [LINKEDIN],
        'alumniOf': [
            {'@type': 'CollegeOrUniversity', 'name': 'University of Kentucky'},
            {'@type': 'CollegeOrUniversity', 'name': 'Johns Hopkins Carey Business School'},
        ],
        'knowsAbout': ['price comparison methodology', 'web analytics', 'data pipelines'],
        'worksFor': {'@id': SITE + '/#org'},
    }


# Visible byline for a comparison / report page.
BYLINE_HTML = ('Analysis by <b><a class="lnk" href="/about#author">%s</a></b> '
               '<a class="lnk" href="/methodology">Method</a>' % NAME)

# Heading on the per-ingredient evidence module.
RATED_BY_HTML = 'Rated by %s' % NAME
