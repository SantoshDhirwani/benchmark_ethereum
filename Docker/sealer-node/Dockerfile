FROM ethereum/client-go:alltools-stable

#expose default ether port
EXPOSE 8545:8545
EXPOSE 30311:30311
#
COPY password password
COPY bootnode bootnode
COPY init-sealer.sh init-sealer.sh
RUN chmod +x init-sealer.sh
ENTRYPOINT ["./init-sealer.sh","123"]