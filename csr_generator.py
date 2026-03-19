from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa


def generate_csr(data):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME,             data["CN"]),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME,       data["O"]),
        x509.NameAttribute(NameOID.COUNTRY_NAME,            data["C"]),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME,  data["ST"]),
        x509.NameAttribute(NameOID.LOCALITY_NAME,           data["L"]),
    ])

    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(subject)
        .sign(key, hashes.SHA256())
    )

    private_key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode()

    return private_key_pem, csr_pem