FROM ethereum/client-go:alltools-stable

#expose default ether port
EXPOSE 8545:8545
EXPOSE 30311:30311
COPY genesis.json genesis.json
COPY password password
COPY bootnode bootnode
COPY init-ether.sh init-ether.sh
RUN chmod +x init-ether.sh
ENTRYPOINT ["./init-ether.sh","123"]