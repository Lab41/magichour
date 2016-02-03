package helper;

public class ArrayHelper {
	
	public static Integer[] toIntegarArray(int[] array) {
		Integer[] intArr = new Integer[array.length];
		for (int i=0; i<array.length; i++) {
			intArr[i] = array[i];
		}
		return intArr;
	}
	
	public static int[] toIntArray(Integer[] array) {
		int[] intArr = new int[array.length];
		for (int i=0; i<array.length; i++) {
			intArr[i] = array[i];
		}
		return intArr;
	}
}
