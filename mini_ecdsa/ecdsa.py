from random import SystemRandom
from random import randrange
from hashlib import sha256


class Point(object):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.inf = False

    @classmethod
    def at_infinity(cls):
        p = cls(0, 0)
        p.inf = True
        return p

    def __str__(self):
        if self.inf:
            return 'Inf'
        else:
            return '(' + str(self.x) + ',' + str(self.y) + ')'

    def __eq__(self, other):
        if self.inf:
            return other.inf
        elif other.inf:
            return self.inf
        else:
            return self.x == other.x and self.y == other.y

    def is_infinite(self):
        return self.inf


class Curve(object):
    def __init__(self, a, b, c, char, exp):
        self.a, self.b, self.c = a, b, c
        self.char, self.exp = char, exp

    def __str__(self):
        if self.a == 0:
            a_term = ''
        elif self.a == 1:
            a_term = ' + x'
        elif self.a == -1:
            a_term = ' - x'
        elif self.a < 1:
            a_term = " - " + str(-self.a) + 'x'
        else:
            a_term = " + " + str(self.a) + 'x'

        if self.b == 0:
            b_term = ''
        elif self.b < 1:
            b_term = " - " + str(-self.b)
        else:
            b_term = " + " + str(self.b)
        #
        # if self.b == 0:
        #     b_term = ''
        # elif self.b == 1:
        #     b_term = ' + x'
        # elif self.b == -1:
        #     b_term = ' - x'
        # elif self.b < 1:
        #     b_term = " - " + str(-self.b) + 'x'
        # else:
        #     b_term = " + " + str(self.b) + 'x'
        #
        # if self.c == 0:
        #     c_term = ''
        # elif self.c < 1:
        #     c_term = " - " + str(-self.c)
        # else:
        #     c_term = " + " + str(self.c)

        self.eq = 'y^2 = x^3 ' + a_term + b_term

        if self.char == 0:
            return self.eq + ' over Q'
        else:
            return self.eq + ' (mod' + str(self.char**self.exp) + ')'

    def discriminant(self):
        a, b, c = self.a, self.b, self.c
        return -4*a*a*a*c + a*a*b*b + 18*a*b*c - 4*b*b*b - 27*c*c

    def order(self, p):
        q = p
        order_p = 1
        while not q.is_infinite():
            q = self.add(p, q)
            order_p += 1
        return order_p

        # assert self.is_valid(g) and g != self.zero
        # for i in range(1, self.q + 1):
        #     if self.mul(g, i) == self.zero:
        #         return i
        #     pass
        # raise Exception("Invalid order")

    def generate(self, p):
        q = p
        orbit = [str(Point.at_infinity())]
        while not q.is_infinite():
            orbit.append(str(q))
            q = self.add(p, q)

        return orbit

    def double(self, p):
        return self.add(p, p)

    def mult(self, p, k):
        if p.is_infinite():
            return p
        elif k == 0:
            return Point.at_infinity()
        elif k < 0:
            return self.mult(self.invert(p), -k)
        else:
            b = bin(k)[2:]
            return self.repeat_additions(p, b, 1)

    def repeat_additions(self, p, b, n):
        if b == '0':
            return Point.at_infinity()
        elif b == '1':
            return p
        elif b[-1] == '0':
            return self.repeat_additions(self.double(p), b[:-1], n + 1)
        elif b[-1] == '1':
            return self.add(p, self.repeat_additions(self.double(p), b[:-1], n + 1))

    def show_points(self):
        return [str(P) for P in self.get_points()]

    def check_curve(self):
        y = (self.char**self.exp)
        if ((4*self.a*self.a*self.a + 27*self.b*self.b) % y) == 0 :
            return False
        else:
            if self.a < y and self.b < y and y > 2:
                return True
            else:
                return False


class CurveOverFp(Curve):
    def __init__(self, a, b, c, p):
        Curve.__init__(self, a, b, c, p, 1)

    def contains(self, p):
        if p.is_infinite():
            return True
        else:
            return (p.y * p.y) % self.char == (p.x * p.x * p.x + self.a * p.x * p.x + self.b * p.x + self.c) % self.char

    def get_points(self):
        points = [Point.at_infinity()]

        for x in range(self.char):
                for y in range(self.char):
                    p = Point(x,y)
                    if (y*y) % self.char == (x*x*x + self.a*x*x + self.b*x + self.c) % self.char:
                        points.append(p)
        return points

    def invert(self, p):
        if p.is_infinite():
            return p
        else:
            return Point(p.x, -p.y % self.char)

    def add(self, p_1, p_2):
        y_diff = (p_2.y - p_1.y) % self.char
        x_diff = (p_2.x - p_1.x) % self.char

        if p_1.is_infinite():
            return p_2
        elif p_2.is_infinite():
            return p_1
        elif x_diff == 0 and y_diff != 0:
            return Point.at_infinity()
        elif x_diff == 0 and y_diff == 0:
            if p_1.y == 0:
                return Point.at_infinity()
            else:
                ld = ((3 * p_1.x * p_1.x + 2 * self.a * p_1.x + self.b) * mult_inv(2 * p_1.y, self.char)) % self.char
        else:
            ld = (y_diff * mult_inv(x_diff, self.char)) % self.char

        nu = (p_1.y - ld * p_1.x) % self.char
        x = (ld * ld - self.a - p_1.x - p_2.x) % self.char
        y = (-ld*x - nu) % self.char

        return Point(x,y)


def divisors(n):
    divs = [0]
    for i in range(1, abs(n) + 1):
        if n % i == 0:
            divs.append(i)
            divs.append(-i)
    return divs


def euclid(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, y, x = euclid(b % a, a)
        return g, x - (b//a)*y, y


def mult_inv(a, n):
    g, x, y = euclid(a, n)
    if g != 1:
        raise ValueError('multiplicative inverse does not exist')
    else:
        return x % n


def hash(message):
    return int(sha256(message).hexdigest(), 16)


def hash_and_truncate(message, n):
    h = hash(message)
    b = bin(h)[2:len(bin(n))]
    return h, int(b, 2)


def generate_keypair(curve, p, n):
    sysrand = SystemRandom()
    d = sysrand.randrange(1, n)
    q = curve.mult(p, d)
    return d, q


def sign(message, curve, p, n, keypair):
    d, q = keypair
    h_txt, z = hash_and_truncate(message, n)

    r, s = 0, 0
    while r == 0 or s == 0:
        k = randrange(1, n)
        R = curve.mult(p, k)
        r = R.x % n
        s = (mult_inv(k, n) * (z + r*d)) % n

    return q, r, s


def verify(message, curve, p, n, sig):
    q, r, s = sig

    if q.is_infinite() or not curve.contains(q):
        return False
    if not curve.mult(q,n).is_infinite():
        return False
    if r > n or s > n:
        return False

    h_txt, z = hash_and_truncate(message, n)

    w = mult_inv(s, n) % n
    u_1 = z * w % n
    u_2 = r * w % n

    c_1 = curve.mult(p, u_1)
    c_2 = curve.mult(q, u_2)
    c = curve.add(c_1, c_2)

    return r % n == c.x % n


def nod(a, b):
    while b:
        a, b = b, a % b
    return a


def simple1(n):
    import math
    dis = int(math.sqrt(n))
    D = range(2, dis + 1)
    for s in D:
        if nod(n, s) != 1:
            return False
    return True


def simple2(a, b):
    if nod(a, b) != 1:
        return False
    return True