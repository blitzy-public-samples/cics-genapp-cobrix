******************************************************************
*  COPYBOOK  : GFOKR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : OK
******************************************************************
 01  RT-FOK-RATING.

          03 RT-FOK-TERRITORY-CODE            PIC X(3).
          03 RT-FOK-CLASS-CODE                PIC X(4).
          03 RT-FOK-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FOK-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FOK-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FOK-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FOK-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FOK-RATED-PREMIUM             PIC 9(9)V9(2).
