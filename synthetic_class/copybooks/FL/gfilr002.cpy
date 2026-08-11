******************************************************************
*  COPYBOOK  : GFILR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : IL
******************************************************************
 01  RT-FIL-RATING.

          03 RT-FIL-TERRITORY-CODE            PIC X(3).
          03 RT-FIL-CLASS-CODE                PIC X(4).
          03 RT-FIL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FIL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FIL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FIL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FIL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FIL-RATED-PREMIUM             PIC 9(9)V9(2).
