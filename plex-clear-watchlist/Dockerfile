# Flytande: `stable-slim` följer Debians nuvarande stable, `trixie-slim` gör
# det inte — den sitter kvar på trixie även när nästa stable släppts. En
# pinnad digest ovanpå det hade dessutom frusit även säkerhetsuppdateringarna
# tills Dependabot råkade bumpa den.
FROM debian:stable-slim

# Python och pip kommer från Debian i stället för från python-imagen. Skälet är
# underhållskedjan: Debians säkerhetsteam patchar dem, och apt-get full-upgrade
# nedan plockar upp rättningarna vid varje bygge. Med uppströms python-image
# väntar man i stället på att den byggs om.
#
# Det avvecklar också fyndklassen som fällde scrapers bygge i augusti:
# uppströms pip deklarerar sina vendrade kopior av setuptools och msgpack i
# pip/_vendor/bom.cdx.json, som Trivy läser som installerade paket. Debians
# python3-pip vendrar samma bibliotek men skickar ingen SBOM, och patchar dem
# via apt.
RUN apt-get update && apt-get full-upgrade -y && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Appens beroenden i ett eget träd. Debians Python-paket får inte ersättas av
# PyPI-versioner — pip kan inte avinstallera dpkg-installerade paket, och
# typing_extensions krockade direkt. Venv:en skapas utan pip, så uppströms
# pips vendrade SBOM aldrig kommer in i imagen; installationen drivs av
# Debians pip utifrån.
RUN python3 -m venv --without-pip /opt/venv \
    && pip --python /opt/venv/bin/python install --no-cache-dir -r requirements.txt
ENV PATH="/opt/venv/bin:$PATH"

COPY plex_clear_watchlist.py .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

ENTRYPOINT ["python", "plex_clear_watchlist.py"]
