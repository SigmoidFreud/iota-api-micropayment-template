from IOTATransferRestRequestTemplate import generate_addresses

def main():
    # wrapper to generate an address
    address = generate_addresses()
    print(address)


if __name__ == "__main__": main()