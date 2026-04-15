#include <SPI.h>
#include <Ethernet2.h>
#include <EthernetUdp2.h>

// === Pin 4094 untuk 7 segment ===
#define STR_JAM D3
#define D_JAM   D0
#define CP_JAM  D8

// === Data segment angka ===
byte angka_jam[10] = {
  B01111111, B00010011, B10111101, B10110111, B11010011,
  B11110110, B11111110, B00110011, B11111111, B11110111
};

byte jam_balik[10] = {
  B11111110, B00110010, B01111101, B01110111, B10110011,
  B11010111, B11011111, B01110010, B11111111, B11110111
};

// === Variabel waktu ===
uint8_t hh = 0, mm = 0, ss = 0;

// ======= Ubah nomor unit 1-40 =======
#define MY_UNIT 46
// =====================================

// MAC unik
byte mac[] = {0xDE, 0xAD, 0xBE, 0xEF, 0x00, MY_UNIT};

// IP statis sesuai subnet Raspberry
IPAddress ip(192, 168, 10, 100 + MY_UNIT);

// UDP settings
unsigned int localPort = 8888;
EthernetUDP Udp;
char packetBuffer[32];
byte buf_jadwal[7];

void setup() {
  Serial.begin(115200);
  
  pinMode(STR_JAM, OUTPUT);
  pinMode(D_JAM, OUTPUT);
  pinMode(CP_JAM, OUTPUT);
  
  hapus_dta_jam();
  
  // --- Tambahan: Animasi angka 0-9 di awal ---
  Serial.println("Testing segments 0-9...");
  test_display();
  hapus_dta_jam(); // Bersihkan layar setelah test
  delay(1000);
  
  Ethernet.init(D4);  // CS W5500 di D4
  Ethernet.begin(mac, ip);
  delay(1000);
  
  Serial.print("Unit ");
  Serial.print(MY_UNIT);
  Serial.print(" Wemos IP: ");
  Serial.println(Ethernet.localIP());
  
  Udp.begin(localPort);
  Serial.print("UDP listening on port ");
  Serial.println(localPort);
}

// Fungsi untuk mengetes angka 0-9 masing-masing 0.5 detik
void test_display() {
  for (int n = 0; n <= 9; n++) {
    // Isi buffer dengan angka yang sama di semua digit
    buf_jadwal[1] = angka_jam[n];
    buf_jadwal[2] = angka_jam[n];
    buf_jadwal[3] = jam_balik[n];
    buf_jadwal[4] = angka_jam[n];
    buf_jadwal[5] = jam_balik[n];
    buf_jadwal[6] = angka_jam[n];
    
    tampil_dta_jam();
    delay(500); // Delay setengah detik
  }
}

void kon_jam() {
  buf_jadwal[1] = angka_jam[hh / 10];
  buf_jadwal[2] = angka_jam[hh % 10];
  buf_jadwal[3] = jam_balik[mm / 10];
  buf_jadwal[4] = angka_jam[mm % 10];
  buf_jadwal[5] = jam_balik[ss / 10];
  buf_jadwal[6] = angka_jam[ss % 10];
}

void tampil_dta_jam() {
  for (byte i = 1; i <= 6; i++) {
    shiftOut(D_JAM, CP_JAM, MSBFIRST, buf_jadwal[i]);
  }
  digitalWrite(STR_JAM, HIGH);
  digitalWrite(STR_JAM, LOW);
}

void hapus_dta_jam() {
  for (byte i = 1; i <= 6; i++) {
    buf_jadwal[i] = 0x00;
    shiftOut(D_JAM, CP_JAM, MSBFIRST, buf_jadwal[i]);
  }
  digitalWrite(STR_JAM, HIGH);
  digitalWrite(STR_JAM, LOW);
}

void loop() {
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    int len = Udp.read(packetBuffer, 32);
    if (len > 0) packetBuffer[len] = 0;

    Serial.print("Received: ");
    Serial.println(packetBuffer);

    int h, m, s;
    if (sscanf(packetBuffer, "%d:%d:%d", &h, &m, &s) == 3) {
      hh = constrain(h, 0, 23);
      mm = constrain(m, 0, 59);
      ss = constrain(s, 0, 59);
      kon_jam();
      tampil_dta_jam();
    }
  }
}