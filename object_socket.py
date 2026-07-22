import pickle
import socket
import struct


class ObjectSender:
    """Clasă responsabilă pentru trimiterea obiectelor Python prin socket-uri TCP/IP.

    Această clasă serializează obiecte Python (matrice OpenCV, cadre video,
    dicționare, etc.) folosind modulele pickle și struct pentru a le transmite
    printr-o conexiune de rețea.
    """

    def __init__(self, ip: str = '127.0.0.1', port: int = 5000):
        """Initializează un socket de tip producător/trimițător (sender).

        Args:
            ip (str, optional): Adresa IP a receptorului la care se va
              conecta. Dacă nu este furnizat, se folosește '127.0.0.1'
              (localhost).
            port (int, optional): Portul de rețea pe care ascultă receptorul.
              Dacă nu este furnizat, se folosește valoarea implicită 5000.
        """
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> None:
        """Stabilește conexiunea TCP/IP cu receptorul (receiver/consumer).

        Încearcă conectarea la adresa IP și portul configurate la inițializare.

        Returns:
            None
        """
        self.socket.connect((self.ip, self.port))

    def send_object(self, obj: object) -> None:
        """Serializează și trimite un obiect Python prin socket-ul de rețea.

        Obiectul este mai întâi transformat în octeți folosind biblioteca
        pickle, după care îi este calculată dimensiunea. Dimensiunea este
        impachetată pe 4 octeți și trimisă înaintea datelor efective pentru a
        permite receptorului să știe câți octeți trebuie să citească.

        Args:
            obj (object): Obiectul Python (ex: imagine/cadru numpy) care urmează
              să fie transmis.

        Returns:
            None
        """
        data = pickle.dumps(obj)
        size = len(data)
        # '>I' înseamnă Big-Endians pe 4 octeți (unsigned int)
        self.socket.sendall(struct.pack('>I', size) + data)

    def close(self) -> None:
        """Închide conexiunea socket activă.

        Eliberează resursele de rețea ocupate de obiectul curent.

        Returns:
            None
        """
        self.socket.close()


class ObjectReceiver:
    """Clasă responsabilă pentru primirea obiectelor Python prin socket-uri TCP/IP.

    Această clasă creează un server socket, ascultă conexiuni de la un ObjectSender,
    reconstituie dimensiunea pachetelor de date și deserializează obiectele
    primite folosind biblioteca pickle.
    """

    def __init__(self, ip: str = '127.0.0.1', port: int = 5000):
        """Initializează un socket de tip consumator/receptor (receiver).

        Args:
            ip (str, optional): Adresa IP pe care serverul va asculta conexiuni.
              Dacă nu este specificată, se folosește '127.0.0.1' (localhost).
            port (int, optional): Portul de rețea pe care se deschide serverul.
              Dacă nu este specificat, valoarea implicită este 5000.
        """
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = None

    def start(self) -> None:
        """Pornește serverul pe IP-ul și portul setat și așteaptă o conexiune.

        Metoda blochează execuția până când un sender (client) se conectează cu
        succes. Odată conectat, păstrează referința conexiunii în atibutul `conn`.

        Returns:
            None
        """
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(1)
        self.conn, _ = self.server_socket.accept()

    def get_object(self) -> object:
        """Așteaptă și citește un obiect Python complet transmis prin rețea.

        Citește mai întâi primii 4 octeți pentru a afla dimensiunea totală a
        obiectului, apoi apelează `_recvall` pentru a colecta toți octeții
        corespunzători înainte de a-i deserializa cu `pickle.loads`.

        Returns:
            object: Obiectul Python deserializat (ex: cadru/frame numpy sau None)
            sau `None` în cazul în care conexiunea a fost întreruptă ori s-a
            produs o eroare la citire.
        """
        try:
            raw_msglen = self._recvall(4)
            if not raw_msglen:
                return None
            msglen = struct.unpack('>I', raw_msglen)[0]
            data = self._recvall(msglen)
            if not data:
                return None
            return pickle.loads(data)
        except Exception:
            return None

    def _recvall(self, n: int) -> bytes:
        """Metodă ajutătoare (privată) ce garantează citirea a exact `n` octeți din socket.

        Deoarece datele dintr-o rețea pot sosi fragmentat în mai multe pachete,
        această metodă apelează în mod repetat `recv` până când adună exact numărul
        dorit de octeți.

        Args:
            n (int): Numărul fix de octeți (bytes) care trebuie citiți din socket.

        Returns:
            bytes: Un obiect de tip octeți (bytes) ce conține exact datele citite,
            sau `None` dacă conexiunea s-a închis neașteptat înainte de a citi tot.
        """
        data = bytearray()
        while len(data) < n:
            packet = self.conn.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return bytes(data)

    def close(self) -> None:
        """Închide conexiunea cu clientul și socket-ul serverului.

        Garantează eliberarea portului de rețea folosit.

        Returns:
            None
        """
        if self.conn:
            self.conn.close()
        self.server_socket.close()
