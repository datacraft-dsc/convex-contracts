# VERSION:      0.1
# DESCRIPTION:  convex-contracts
# AUTHOR:       Datacraft
# COMMENTS:
#       This deploys the starfish contracts on the convex development network
# USAGE:
#       docker run docker.pkg.github.com/datacraft-dscF/convex-contracts/deploy-testing:latest

FROM alpine:latest

RUN apk add --no-cache gcc git python3 py3-pip python3-dev linux-headers libc-dev libffi-dev openssl-dev make py3-gunicorn

ENV HOME=/home/convex_contracts
ENV IGNORE_VENV=1

WORKDIR $HOME
ADD . $HOME

RUN make install

CMD ./tools/convex_contract_tool.py \
    --keyfile=./tests/resources/account_key_files/local/5288fec4153b702430771dfac8aed0b21cafca4344dae0d47b97f0bf532b3306.pem \
    --password=secret \
    --auto-topup \
    deploy
