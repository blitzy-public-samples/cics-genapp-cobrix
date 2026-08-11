******************************************************************
*  COPYBOOK  : GFMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : MS
******************************************************************
 01  RT-FMS-RATING.

          03 RT-FMS-TERRITORY-CODE            PIC X(3).
          03 RT-FMS-CLASS-CODE                PIC X(4).
          03 RT-FMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FMS-RATED-PREMIUM             PIC 9(9)V9(2).
