from IOTATransferRestRequestTemplate import generate_addresses

def main():
    # wrapper to generate an address
    address = generate_addresses(uri="http://85.93.93.110:14265/")
    print(address)


if __name__ == "__main__": main()