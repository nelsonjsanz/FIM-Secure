#include <stdio.h>
#include <stdlib.h>
#include <windows.h>
#include <wincrypt.h>

#define BUFSIZE 4096

void print_error(const char* msg) {
    fprintf(stderr, "[ERROR C] %s\n", msg);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <ruta_archivo>\n", argv[0]);
        return 1;
    }

    FILE *f = fopen(argv[1], "rb");
    if (!f) {
        print_error("No se pudo abrir el archivo especificado.");
        return 1;
    }

    HCRYPTPROV hProv = 0;
    HCRYPTHASH hHash = 0;
    BYTE rgbFile[BUFSIZE];
    DWORD cbRead = 0;
    BYTE rgbHash[32];
    DWORD cbHash = 32;
    CHAR rgbDigits[] = "0123456789abcdef";
    int success = 0;

    // Cambiado a PROV_RSA_AES (24) para permitir soporte completo de SHA-256
    if (!CryptAcquireContext(&hProv, NULL, NULL, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) {
        fclose(f);
        print_error("Error al adquirir el contexto criptográfico.");
        return 1;
    }

    if (!CryptCreateHash(hProv, CALG_SHA_256, 0, 0, &hHash)) {
        CryptReleaseContext(hProv, 0);
        fclose(f);
        print_error("Error al crear el objeto hash.");
        return 1;
    }

    while ((cbRead = fread(rgbFile, 1, BUFSIZE, f)) > 0) {
        if (!CryptHashData(hHash, rgbFile, cbRead, 0)) {
            print_error("Error al procesar los datos del archivo.");
            success = 1;
            break;
        }
    }

    fclose(f);

    if (!success && CryptGetHashParam(hHash, HP_HASHVAL, rgbHash, &cbHash, 0)) {
        for (DWORD i = 0; i < cbHash; i++) {
            printf("%c%c", rgbDigits[rgbHash[i] >> 4], rgbDigits[rgbHash[i] & 0xf]);
        }
        printf("\n");
    } else {
        success = 1;
    }

    CryptDestroyHash(hHash);
    CryptReleaseContext(hProv, 0);

    return success;
}