volatile unsigned long isrCount = 0;
unsigned long lastTick = 0;

const unsigned long INTERVAL_MS = 50; // 
const byte pulsePin   = 2;
const byte duetOutPin = 8;
const byte ledPin     = LED_BUILTIN;

void impulse() {
  isrCount++;
}

void setup() {
  Serial.begin(9600);

  pinMode(pulsePin, INPUT);
  pinMode(duetOutPin, OUTPUT);
  pinMode(ledPin, OUTPUT);

  digitalWrite(duetOutPin, LOW);
  digitalWrite(ledPin, LOW);

  attachInterrupt(digitalPinToInterrupt(pulsePin), impulse, FALLING);

  Serial.println("Pulse counter started (Uno R4)");
}

void loop() {
  unsigned long now = millis();

  if (now - lastTick >= INTERVAL_MS) {
    lastTick += INTERVAL_MS;

    noInterrupts();
    unsigned long windowCount = isrCount;
    isrCount = 0;
    interrupts();

    Serial.print("Counts: ");
    Serial.println(windowCount);

  if (windowCount >= 3) {
    // Turn ON voltage and LED
    digitalWrite(duetOutPin, HIGH);
    digitalWrite(ledPin, HIGH);
    // delay(1000);
  } else {
    // Turn OFF
    digitalWrite(duetOutPin, LOW);
    digitalWrite(ledPin, LOW);
  }
  }
}