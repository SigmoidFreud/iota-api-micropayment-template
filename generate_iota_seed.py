from IOTATransferRestRequestTemplate import generate_addresses

def main():
    # wrapper to generate an address
    address = generate_addresses(uri="YOUR SERVER ADDRESS GOES HERE")
    print(address)


if __name__ == "__main__": main()