#! /bin/sh

buildout_bin=`dirname $0`/bin
PATH=$buildout_bin:$PATH
I18NDOMAIN="collective.cover"
BASE_DIRECTORY="src/collective/cover"

# Synchronise the templates and scripts with the .pot.
i18ndude rebuild-pot --pot ${BASE_DIRECTORY}/locales/${I18NDOMAIN}.pot \
    --merge ${BASE_DIRECTORY}/locales/manual.pot \
    --create ${I18NDOMAIN} \
    ${BASE_DIRECTORY}

# Synchronise the resulting .pot with all .po files
for po in ${BASE_DIRECTORY}/locales/*/LC_MESSAGES/${I18NDOMAIN}.po; do
    i18ndude sync --pot ${BASE_DIRECTORY}/locales/${I18NDOMAIN}.pot $po
done

# Synchronise the templates and scripts with the .pot.
i18ndude rebuild-pot --pot ${BASE_DIRECTORY}/locales/plone.pot \
    --create plone \
    ${BASE_DIRECTORY}/configure.zcml \
    ${BASE_DIRECTORY}/profiles/default

# Synchronise the plone's pot file (Used for the workflows)
for po in ${BASE_DIRECTORY}/locales/*/LC_MESSAGES/plone.po; do
    i18ndude sync --pot ${BASE_DIRECTORY}/locales/plone.pot $po
done

# Report of errors and suspect untranslated messages
i18ndude find-untranslated -n ${BASE_DIRECTORY}
