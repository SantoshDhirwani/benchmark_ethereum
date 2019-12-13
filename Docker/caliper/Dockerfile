FROM hyperledger/caliper:0.2.0

COPY init-caliper.sh init-caliper.sh
RUN chmod +x init-caliper.sh


ENV CALIPER_BIND_SUT=fabric
ENV CALIPER_BIND_SDK=1.4.0

ADD config ./workspace

RUN npm i web3

ENTRYPOINT ["./init-caliper.sh","123"]