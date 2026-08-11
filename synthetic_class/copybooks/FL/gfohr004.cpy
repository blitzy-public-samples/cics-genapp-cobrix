******************************************************************
*  COPYBOOK  : GFOHR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : OH
******************************************************************
 01  RT-FOH-RATING.

          03 RT-FOH-TERRITORY-CODE            PIC X(3).
          03 RT-FOH-CLASS-CODE                PIC X(4).
          03 RT-FOH-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FOH-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FOH-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FOH-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FOH-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FOH-RATED-PREMIUM             PIC 9(9)V9(2).
