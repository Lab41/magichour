package loginsight.core;

public class DoublePair {
    private double first;
    private double second;

    public DoublePair(double first, double second) {
        this.first = first;
        this.second = second;
    }

    @Override
	public int hashCode() {
        int hashFirst = (int)first;
        int hashSecond = (int)second;

        return (hashFirst + hashSecond) * hashSecond + hashFirst;
    }

    @Override
	public boolean equals(Object other) {
        if (other instanceof Pair) {
        	DoublePair otherPair = (DoublePair) other;
                return 
                ((  this.first == otherPair.first ||
                        ( this.first == otherPair.first)) &&
                 (      this.second == otherPair.second ||
                        (  this.second == otherPair.second)) );
        }

        return false;
    }

    @Override
	public String toString()
    { 
           return "(" + first + ", " + second + ")"; 
    }

    public double getFirst() {
        return first;
    }

    public void setFirst(double first) {
        this.first = first;
    }

    public double getSecond() {
        return second;
    }

    public void setSecond(double second) {
        this.second = second;
    }
}
