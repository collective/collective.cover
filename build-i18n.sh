#!/bin/sh

I18NDUDE=bin/i18ndude
DOMAIN="collective.cover"
I18NPATH="src/$DOMAIN/src/collective/cover"

$I18NDUDE rebuild-pot --pot ${I18NPATH}/locales/${DOMAIN}.pot --create ${DOMAIN} ${I18NPATH}
$I18NDUDE sync --pot ${I18NPATH}/locales/${DOMAIN}.pot ${I18NPATH}/locales/*/LC_MESSAGES/${DOMAIN}.po

## Don't automatically run the rebuild for the "plone" domain, as it puts too
## much message strings into it.
#DOMAIN=plone
#$I18NDUDE rebuild-pot --pot $I18NPATH/locales/$DOMAIN.pot --merge $I18NPATH/locales/merge-plone.pot --create $DOMAIN $I18NPATH
#$I18NDUDE sync --pot $I18NPATH/locales/$DOMAIN.pot $I18NPATH/locales/*/LC_MESSAGES/$DOMAIN.po
