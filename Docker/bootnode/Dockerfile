FROM ethereum/client-go:alltools-stable

#expose default ether port
EXPOSE 30311:30311

COPY init-bootnode.sh init-bootnode.sh
COPY boot.key boot.key
RUN chmod +x init-bootnode.sh

ENTRYPOINT ["./init-bootnode.sh"]